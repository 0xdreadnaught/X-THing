# X-TeleHunting (X-THing)

X-THing is an Telegram hunting tool that merges functionalities from two major projects: a refactored fork of [Flare](https://flare.io)'s Telehunting project [here](https://github.com/Flared/telehunting) and [nietowl](https://github.com/nietowl)'s TeleHuntX project [here](https://github.com/nietowl/TeleHuntX). This tool lets users efficiently search and crawl through Telegram messages and channels in multiple languages.

## Features

### Unified Telegram Hunting
X-THing combines the core functionalities of both **Telehunting** and **TeleHuntX**, providing an all-in-one solution for Telegram message searching and crawling.

### Multilingual Search with Google Translate
With **Google Translation** integration, users can search for messages in multiple languages simultaneously. X-THing automatically translates search queries into the selected languages and displays unique and total matches.

### UI Enhancements
The search UI now leverages ellipses pagination  for smoother navigation.

### Debug Info
While disabled by default, the logging is in place for searches, just comment out the logging near the start of the script and update the main function to True.

### Modular Codebase
Instead of one large script, things have been broken apart into more manageable subscripts.

## Planned Features

X-THing is actively being developed, with future enhancements planned across both **X-Crawler** and **X-Thing** modules such as send colors, suppressing harvested messages/channels, etc.
Bug fixes are also planned, like squashing the hypercorn output on launch.

## Known Issues

There may be some false positives in the search results due to poor translation attempts. Things like malware names really screw with it. The search logic will be refined, hopefully adding more dynamic features... maybe even regex...

## Installation

### Prerequisites

- Python 3.7+
- A Telegram API ID and Hash. You can get these from [Telegram's API website](https://my.telegram.org/auth).

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

Alternatively, you can pass the API credentials as flags when running the tool (not advised).

### Running the Application

To launch the **X-THing** interface:

```
python x-thing.py
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
![image](https://github.com/user-attachments/assets/b63c1ab7-07eb-4a32-9b3e-8b66dccd7eb9)

* #### X-THing Dashboard:
![image](https://github.com/user-attachments/assets/37a6f6da-f286-4bdf-80c0-86ccf2d74fc5)

* #### X-Crawler starting a crawl:
![image](https://github.com/user-attachments/assets/33bc504f-5c5a-4bd9-bf01-1d43001b31a7)


