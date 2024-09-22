# X-TeleHunting (X-THing)

X-THing is a Telegram hunting tool that merges functionalities from two projects: a refactored fork of [Flare](https://flare.io)'s Telehunting [here](https://github.com/Flared/telehunting) and [nietowl](https://github.com/nietowl)'s TeleHuntX [here](https://github.com/nietowl/TeleHuntX). This tool lets users efficiently search and crawl through Telegram messages and channels in multiple languages.

**Note:** Your mileage may vary as this is a heavily bastardized version of the two projects. I have introduced an equal number of features/bugs.

[![CodeQL](https://github.com/0xdreadnaught/X-THing/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/0xdreadnaught/X-THing/actions/workflows/github-code-scanning/codeql)
[![Bandit](https://github.com/0xdreadnaught/X-THing/actions/workflows/bandit.yml/badge.svg)](https://github.com/0xdreadnaught/X-THing/actions/workflows/bandit.yml)

## Features

### Unified Telegram Hunting
Not quite yet lol. While you can leverage both scripts at the same time, the goal is the have one launch script, and have access to a dynamic number of x-crawler instances inside the webUI. Allowing for parsing multiple tailored campaigns.

### Multilingual Search with Google Translate
With **Google Translation** integration, users can search for messages in multiple languages simultaneously. X-THing automatically translates search queries into the selected languages and displays unique and total matches.

### UI Enhancements
The search UI now leverages ellipses pagination for smoother navigation.

### Debug Info
While disabled by default, `x-thing.py` has logging in place for some background task data. Comment out the logging near the start of the script and update the main function to True.

### Modular Codebase:
The goal is to try and keep things pretty modular so they're easy to maintain/customize.

- **x-crawler.py**: Responsible for crawling Telegram channels based on the defined configuration, searching for messages matching keywords, and handling channel traversal.
- **x-thing.py**: The main entry point of the application, which hosts the dashboard interface, processes search requests, and interacts with other modules.
- **batch_processor.py**: Manages batch processing of messages, handles sentiment analysis, saves batches to CSV files, and generates a final report from the aggregated messages using a sentiment analyzer.
- **channel_manager.py**: Manages discovered, joined, and processed channels. Tracks affiliations between channels and manages the list of channels yet to be processed.
- **config.json**: Stores initial configuration parameters, such as starting channels, search terms, and batch size for message retrieval.
- **config.py**: Handles configuration loading and creation. Provides functions to load an existing config or create a default one if none exists.
- **message_processor.py**: Contains a custom cybersecurity sentiment analyzer based on the NLTK sentiment intensity analyzer. It extends the analyzer with a cybersecurity lexicon to evaluate the sentiment of messages in a cybersecurity context.
- **report_generator.py**: Generates a detailed sentiment analysis report from a DataFrame of messages, including sentiment categorization and scoring. It outputs the report to both a text file and the console.
- **telegram_client.py**: Implements a wrapper around the Telethon Telegram client. It manages joining channels, scraping messages, handling flood control, and parsing channel links.
- **transcheck.py**: Provides functionality to translate English text to German using the Google Translator library. Includes a simple interactive translation loop for command-line usage.
- **utils.py**: Contains various utility functions for colored console printing, displaying banners, and ensuring NLTK data availability. Also includes functions for categorized sentiment coloring.
- **static/**: Contains static assets for the web interface.
  - **script.js**: Manages the frontend behavior and interactions of the X-THing dashboard.
  - **styles.css**: Defines the styling for the X-THing web interface.
- **templates/**: Contains HTML templates used by the web interface.
  - **index.html**: The main template for the X-THing dashboard.

## Planned Features

X-THing is actively being developed, with future enhancements planned across both **X-Crawler** and **X-Thing** modules such as:

- Add a handful of source languages.
- Get/display the sender's name color.
- Cleanup `x-thing.py` output. (hypercorn warnings)
- Cleanup `x-crawler.py` output. (harvested messages/channels)
- Bug fixes.

## Bugs

- ~~When searching eng>eng it tries to translate when it shouldn't, sometimes resulting in a bad search string.~~
  - ~~Things like malware names screw with it, ex: `mispadu` becomes `mispada`.~~
- ~~The `--rate-limit` flag added to `x-crawler.py` doesn't seem to work below 600.~~
  - ~~Default rate of operations is too much for prolonged use. Telethon should handle this but Telegram may have changed things a bit.~~

## Installation

### Prerequisites

- Python 3.7+
- A Telegram API ID and hash. You can get these from [Telegram's API website](https://my.telegram.org/auth).

### Install Dependencies
First, clone the repository and navigate into the directory. Then install the required dependencies using:

```
pip install -r requirements.txt
```

### Configuration

Ensure you have a `credentials.json` file in the root directory with the following structure:

```
{
    "api_id": "YOUR_API_ID",
    "api_hash": "YOUR_API_HASH",
    "phone_number": "YOUR_PHONE_NUMBER"
}
```

*Alternatively, you can pass the API credentials as flags when running the tool (not advised).

Update your starting channels and search terms in `config.json`:
```
{
    "initial_channel_links": [
      "https://t.me/<channel1>",
      "https://t.me/<channel2>",
      "https://t.me/<channeln>"
    ],
    "message_keywords": ["hackers", "CVE", "malware", "exploit", "etc"],
    "batch_size": 100
}
```

### Running the Application

To launch the **X-THing** interface:

```
#full send
python x-thing.py

#rate limited (5s/req)
python x-thing.py --rate-limit 5
```

For **X-Crawler** functionality, run:

```
#with credentials.json
python ./x-crawler.py --config ./config.json --message-depth 100 --channel-depth 2

#without credentials.json
python ./x-crawler.py --config ./config.json --message-depth 100 --channel-depth 2 --api-id <your id> --api-hash <your hash> --phone-number <your number>
```

**Note:** You may still need to enter your number and a TOTP at runtime due to TG safety measures. 

### Runtime

* #### X-THing hosting the dashboard and processing search requests:
![image](https://github.com/user-attachments/assets/a151f474-ada1-49ca-8fff-5da2ab45a477)

* #### X-THing Dashboard:
![image](https://github.com/user-attachments/assets/dfef95b1-e5c3-4c39-aee1-6ab9d9525bdb) 
![image](https://github.com/user-attachments/assets/c3774d3b-bf75-4173-a8d1-7fdffce33fa7)

* #### X-THing user search:
![image](https://github.com/user-attachments/assets/4602752a-11fb-4ef0-9ad5-4998287655c2)
![image](https://github.com/user-attachments/assets/6338022e-409d-4f60-bf35-00c2c78c06a4)

* #### X-Crawler starting a crawl:
![image](https://github.com/user-attachments/assets/33bc504f-5c5a-4bd9-bf01-1d43001b31a7)

* #### X-Crawler joining channels:
![image](https://github.com/user-attachments/assets/d0e9e3f6-1068-45eb-a611-747be28d9b05)
