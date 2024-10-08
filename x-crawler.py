import asyncio
import argparse
import json
from config import load_config, create_default_config
from telegram_client import create_client, TelegramClientWrapper
from channel_manager import ChannelManager
from message_processor import CybersecuritySentimentAnalyzer
from batch_processor import BatchProcessor
from utils import print_header, print_info, print_error, banner, ensure_nltk_data
from datetime import datetime
import os
from tqdm import tqdm
import time

# Function to read credentials from the credentials.json file
def load_credentials(file_path='./credentials.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                credentials = json.load(file)
                return credentials
            except json.JSONDecodeError:
                print_error(f"Failed to decode JSON from {file_path}. Please ensure it's valid JSON.")
                return None
    else:
        print_error(f"Credentials file '{file_path}' not found.")
        return None

async def run_scraper(client_wrapper, config, message_depth, channel_depth, rate_limit, show_messages):
    channel_manager = ChannelManager()
    cybersecurity_sia = CybersecuritySentimentAnalyzer()
    batch_processor = BatchProcessor(cybersecurity_sia=cybersecurity_sia)
    
    for link in config['initial_channel_links']:
        channel_manager.add_channel(link)
    
    start_time = datetime.now()
    print_header(f"Scraping started at {start_time}")

    depth = 0
    while channel_manager.has_unprocessed_channels() and depth < channel_depth:
        print_header(f"Crawling at depth {depth + 1}/{channel_depth}")
        channel_manager.display_status()
        
        await process_channels(client_wrapper, channel_manager, message_depth, config['message_keywords'], batch_processor, rate_limit, show_messages)
        
        depth += 1
    
    end_time = datetime.now()
    duration = end_time - start_time
    print_header(f"\nScraping completed at {end_time}")
    print_info(f"Total duration: {duration}")
    print_info(f"Total messages scraped: {batch_processor.total_messages}")
    print_info(f"Total channels processed: {len(channel_manager.processed_channels)}\n")

    batch_processor.finalize()

async def process_channels(client_wrapper, channel_manager, message_depth, keywords, batch_processor, rate_limit, show_messages):
    previous_time = time.monotonic()  # Initialize outside of the loop
    first_operation = True  # Track if it's the first operation

    while channel_manager.has_unprocessed_channels():
        # Only apply rate limit if it's not the first operation
        if not first_operation:
            current_time = time.monotonic()
            time_delta = current_time - previous_time
            
            if rate_limit > 0 and time_delta < rate_limit:
                remaining_time = rate_limit - time_delta
                print(f"Applying rate limit of {remaining_time:.2f} seconds before moving to the next channel.")
                for _ in tqdm(range(int(remaining_time)), desc="Waiting", unit="s"):
                    await asyncio.sleep(1)
                    
            # Update previous_time after the rate limit has been applied
            previous_time = time.monotonic()

        link = channel_manager.get_next_channel()
        affiliated_channel = channel_manager.get_affiliation(link)
        try:
            join_success = await client_wrapper.join_channel(channel_manager, link)
            if join_success:
                entity = await client_wrapper.get_entity(link)
                entity_messages, channel_name = await client_wrapper.scrape_messages(entity, message_depth, keywords, channel_manager, affiliated_channel)
                
                if show_messages:
                    # If --show-messages is passed, print each message
                    for message in entity_messages:
                        print_info(f"Message from {channel_name}: {message[2]}")  # Assuming message[2] contains the actual message content
                else:
                    # If --show-messages is NOT passed, show total count instead
                    print_info(f"Total messages from {channel_name}: {len(entity_messages)}")
                
                batch_processor.add_messages(entity_messages, channel_name, affiliated_channel)
            else:
                print_error(f"Skipping entity {link} due to joining failure")
        except Exception as e:
            print_error(f"Failed to process entity {link}: {e}")
        finally:
            channel_manager.mark_as_processed(link)

        # Set first_operation to False after the first iteration completes
        if first_operation:
            first_operation = False
            previous_time = time.monotonic()  # Set the time after the first operation finishes

if __name__ == "__main__":
    banner()
    ensure_nltk_data()

    parser = argparse.ArgumentParser(description='Telegram Content Crawler')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file')
    parser.add_argument('--message-depth', type=int, default=1000, help='Number of messages to crawl per channel')
    parser.add_argument('--channel-depth', type=int, default=2, help='Depth of channel crawling')
    parser.add_argument('--api-id', type=str, help='API ID for Telegram client')
    parser.add_argument('--api-hash', type=str, help='API hash for Telegram client')
    parser.add_argument('--phone-number', type=str, help='Phone number for Telegram client')
    parser.add_argument('--rate-limit', type=float, default=1.0, help='Rate limit in seconds between channel processing')
    parser.add_argument('--show-messages', action='store_true', help='Display messages scraped from channels')  # Added flag here
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)
    if config is None:
        user_input = input(f"Config file '{args.config}' not found. Create a default config? (y/n): ")
        if user_input.lower() == 'y':
            config = create_default_config(args.config)
        else:
            print_error("Please provide a valid config file. Exiting.")
            exit(1)

    # Load credentials from file if API ID, hash, or phone number not supplied via CLI
    credentials = load_credentials()
    api_id = args.api_id or (credentials and credentials.get('api_id'))
    api_hash = args.api_hash or (credentials and credentials.get('api_hash'))
    phone_number = args.phone_number or (credentials and credentials.get('phone_number'))

    if not api_id or not api_hash or not phone_number:
        print_error("API ID, API Hash, and Phone Number are required. Please provide them either via CLI or credentials.json.")
        exit(1)

    # Create Telegram client
    client = create_client(api_id, api_hash, phone_number)
    client_wrapper = TelegramClientWrapper(client)

    # Run the scraper
    with client:
        client.loop.run_until_complete(run_scraper(client_wrapper, config, args.message_depth, args.channel_depth, args.rate_limit, args.show_messages))
