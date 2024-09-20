import asyncio
import json
from quart import Quart, render_template, request, jsonify
from telethon import TelegramClient, types
from telethon.tl.types import InputMessagesFilterEmpty
import os
from deep_translator import GoogleTranslator
import logging

app = Quart(__name__)

# Set logging level to WARNING or ERROR to avoid sensitive debug/info logs
logging.basicConfig(level=logging.WARNING)

log = logging.getLogger('quart.app')
log.setLevel(logging.WARNING)

logging.getLogger('hypercorn').setLevel(logging.WARNING)
logging.getLogger('telethon').setLevel(logging.WARNING)

# Function to map certain languages to their Google Translate codes
def map_language_code(lang_code):
    language_mapping = {
        'he': 'iw',  # Hebrew in Google Translate
    }
    return language_mapping.get(lang_code, lang_code)

# Function to display 'iw' as 'he' in terminal output
def display_language_code(lang_code):
    if lang_code == 'iw':
        return 'he'
    return lang_code

# Function to read API credentials from a JSON file
def read_credentials_from_file(file_path):
    with open(file_path, 'r') as file:
        credentials = json.load(file)
    return credentials

# Context manager for the TelegramClient
class TelegramClientContext:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None

    async def __aenter__(self):
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        print("Starting Telegram client...")
        await self.client.start()
        print("Telegram client started.")
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            print("Closing Telegram client...")
            await self.client.disconnect()
            print("Telegram client closed.")

# Function to translate text using GoogleTranslator from deep_translator
def translate_text(text, source_language, target_language):
    try:
        target_language = map_language_code(target_language)  # Ensure correct language code
        source_language = map_language_code(source_language)  # Map the source language

        # Skip translation if source and target languages match
        if source_language == target_language:
            print(f"Skipping translation: Source and target languages are the same ({display_language_code(target_language)}).")
            return text

        # Proceed with translation if languages differ
        translator = GoogleTranslator(source=source_language, target=target_language)
        translated_text = translator.translate(text)

        print(f"Translation complete: '{text}' to {display_language_code(target_language)}: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

async def perform_search(client, search_query, limit=50):
    search_results = []
    try:
        async for message in client.iter_messages(entity=None, search=search_query, limit=limit):
            try:
                if not message.text and not message.forward:  # Skip messages with no content and no forward
                    continue
                
                sender_info = {
                    'id': message.sender_id,
                    'title': 'Unknown',
                    'type': 'Unknown',
                    'color': None
                }

                try:
                    sender = await message.get_sender()
                    if sender:
                        if isinstance(sender, types.User):
                            full_name = []
                            if sender.first_name:
                                full_name.append(sender.first_name)
                            if sender.last_name:
                                full_name.append(sender.last_name)
                            sender_info['title'] = ' '.join(full_name) if full_name else sender.username or 'Unknown User'
                            sender_info['type'] = 'User'

                            # Extract the PeerColor if available
                            if hasattr(sender, 'peer_color'):
                                peer_color = sender.peer_color
                                if isinstance(peer_color, types.PeerColor):
                                    sender_info['color'] = f'{peer_color.color:06x}'  # Convert to hex string
                                    print(f"Sender color: {sender_info['color']}")  # Debug print
                                else:
                                    print("No PeerColor available for this sender.")  # Debug print
                        elif isinstance(sender, types.Channel):
                            sender_info['title'] = sender.title or 'Unknown Channel'
                            sender_info['type'] = 'Channel'
                        else:
                            sender_info['title'] = getattr(sender, 'title', None) or getattr(sender, 'first_name', None) or 'Unknown'
                            sender_info['type'] = type(sender).__name__
                    else:
                        sender_info['title'] = message.sender.username if message.sender else 'Unknown'
                except Exception as sender_error:
                    print(f"Error getting sender info: {str(sender_error)}")
                    try:
                        if message.chat:
                            sender_info['title'] = message.chat.title or 'Unknown Chat'
                            sender_info['type'] = 'Chat'
                    except:
                        pass

                urls = []
                if message.entities:
                    for entity in message.entities:
                        if isinstance(entity, types.MessageEntityUrl):
                            url_start = entity.offset
                            url_end = entity.offset + entity.length
                            url = message.text[url_start:url_end]
                            urls.append(url)

                attached_files = []
                if message.media:
                    if isinstance(message.media, types.MessageMediaPhoto):
                        media_info = {
                            'type': 'Photo',
                            'file': 'Unknown',
                            'mime_type': 'image/jpeg',
                            'size': 0
                        }
                        attached_files.append(media_info)

                forward_info = None
                if message.forward:
                    forward_sender = None
                    if message.forward.sender:
                        forward_sender = getattr(message.forward.sender, 'username', None) or \
                                         getattr(message.forward.sender, 'title', None) or \
                                         'Unknown Sender'
                    elif message.forward.from_id:
                        forward_sender = str(message.forward.from_id)

                    forward_info = {
                        'forwarded_from': forward_sender,
                        'forwarded_text': message.text
                    }

                content = message.text
                webpage_preview = ""

                if message.web_preview:
                    if message.web_preview.description:
                        webpage_preview = message.web_preview.description
                    elif message.web_preview.title:
                        webpage_preview = message.web_preview.title

                full_content = f"{content}\n{webpage_preview}".strip()

                content_beautified = None
                try:
                    content_json = json.loads(message.text)
                    content_beautified = json.dumps(content_json, indent=4, sort_keys=True)
                except json.JSONDecodeError:
                    pass

                if message.chat:
                    if message.chat.username:
                        post_url = f'https://t.me/{message.chat.username}/{message.id}'
                    else:
                        post_url = f'https://t.me/c/{str(message.chat.id)[4:]}/{message.id}'
                else:
                    post_url = "Unknown"

                search_results.append({
                    'message_id': message.id,
                    'date': str(message.date),
                    'sender': sender_info['title'],
                    'sender_type': sender_info['type'],
                    'sender_color': sender_info['color'],
                    'content': full_content,
                    'content_beautified': content_beautified,
                    'in_message_urls': urls,
                    'attached_files': attached_files,
                    'post_url': post_url,
                    'forward_info': forward_info
                })

            except Exception as message_error:
                print(f"Error processing message: {str(message_error)}")

    except Exception as e:
        print(f"Error in perform_search: {str(e)}")

    return search_results

async def perform_user_search(client, username, limit=50):
    search_results = []
    user_entity = None
    
    try:
        # First attempt to directly resolve the user entity
        try:
            user_entity = await client.get_input_entity(username)
            user_id = user_entity.user_id
        except Exception as e:
            print(f"Direct resolution failed for user '{username}': {str(e)}")
            return search_results
            
        # If the user is resolved, search their messages in all channels
        if user_entity:
            print(f"User '{username}' resolved to ID: {user_id}. Proceeding with message search...")

            # Iterate over all channels/groups you're connected to
            async for dialog in client.iter_dialogs():
                if dialog.is_channel or dialog.is_group:
                    print(f"Searching in {dialog.name} (ID: {dialog.id})...")

                    try:
                        # Retrieve messages without applying server-side filters (fetch all)
                        async for message in client.iter_messages(dialog, limit=limit):
                            if message.sender_id == user_id:
                                sender_info = {
                                    'id': message.sender_id,
                                    'title': username,
                                    'type': 'User',
                                    'color': None
                                }

                                content = message.text or 'No content'

                                search_results.append({
                                    'message_id': message.id,
                                    'date': str(message.date),
                                    'sender': f"{sender_info['title']} [{sender_info['id']}]",
                                    'sender_type': sender_info['type'],
                                    'content': content,
                                    'post_url': f'https://t.me/c/{str(message.chat_id)[4:]}/{message.id}' if message.chat else 'Unknown'
                                })

                    except Exception as e:
                        print(f"Error fetching messages in {dialog.name}: {str(e)}")
        else:
            print(f"User '{username}' not found in any dialogs or channels.")
            
    except Exception as e:
        print(f"Error in user search: {str(e)}")

    return search_results

async def perform_multi_language_search(client, search_query, languages, source_language, search_by_user):
    all_results = []
    total_message_count = 0
    
    print(f"Input: {search_query}")
    
    if search_by_user:
        # Perform search by username if the flag is set
        search_results = await perform_user_search(client, search_query)
        total_message_count = len(search_results)
        all_results.extend(search_results)
    else:
        # Otherwise, perform normal message content search
        for lang in languages:
            if lang != source_language:  # Use source language provided by user
                translated_query = translate_text(search_query, source_language, lang)
            else:
                translated_query = search_query

            print(f"Searching for '{translated_query}'...")
            lang_results = await perform_search(client, translated_query)
            search_count = len(lang_results)
            total_message_count += search_count

            print(f"Found {search_count} messages for '{translated_query}'...")

            all_results.extend(lang_results)

            print(f"Completed search for '{translated_query}'...")
    
    print(f"Total matching messages found: {total_message_count}")
    
    return all_results

@app.route('/')
async def home():
    return await render_template('index.html')

@app.route('/search', methods=['POST'])
async def search():
    if request.method == 'POST':
        try:
            request_data = await request.json
            search_query = request_data.get('q')
            languages = request_data.get('languages', ['en'])
            source_language = request_data.get('source_language', 'en')  # Get source language from request
            search_by_user = request_data.get('search_by_user', False)  # Check if the search is by user
            page = request_data.get('page', 1)
            results_per_page = 10

            if not search_query:
                return jsonify({'error': 'Search query not provided'})

            api_credentials_file = 'credentials.json'
            if not os.path.exists(api_credentials_file):
                raise FileNotFoundError(f"API credentials file '{api_credentials_file}' not found.")

            api_credentials = read_credentials_from_file(api_credentials_file)

            async with TelegramClientContext(api_credentials['api_id'], api_credentials['api_hash']) as client:
                search_results = await perform_multi_language_search(client, search_query, languages, source_language, search_by_user)

            # If there's an error, return it to the UI
            if isinstance(search_results, dict) and 'error' in search_results:
                return jsonify(search_results)

            start_index = (page - 1) * results_per_page
            end_index = start_index + results_per_page
            paginated_results = search_results[start_index:end_index]

            return jsonify({
                'results': paginated_results,
                'total_results': len(search_results),
                'page': page,
                'total_pages': -(-len(search_results) // results_per_page)
            })

        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/translate', methods=['POST'])
async def translate():
    if request.method == 'POST':
        try:
            request_data = await request.json
            text = request_data.get('text')
            target_lang = request_data.get('target_lang')
            source_lang = request_data.get('source_lang', 'en')  # Pass source language as well

            if not text or not target_lang:
                return jsonify({'error': 'Text or target language not provided'})

            translated_text = translate_text(text, source_lang, target_lang)

            return jsonify({'translated_text': translated_text})

        except Exception as e:
            return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False)
