# X-TeleHunting (X-THing)

X-THing is a Telegram hunting tool that merges functionalities from two projects: a refactored fork of [Flare](https://flare.io)'s Telehunting [here](https://github.com/Flared/telehunting) and [nietowl](https://github.com/nietowl)'s TeleHuntX [here](https://github.com/nietowl/TeleHuntX). This tool lets users efficiently search and crawl through Telegram messages and channels in multiple languages.

**Note:** Your mileage may vary as this is a heavily bastardized version of the two projects. I have introduced an equal number of features/bugs.

[![CodeQL](https://github.com/0xdreadnaught/X-THing/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/0xdreadnaught/X-THing/actions/workflows/github-code-scanning/codeql)
[![Bandit](https://github.com/0xdreadnaught/X-THing/actions/workflows/bandit.yml/badge.svg)](https://github.com/0xdreadnaught/X-THing/actions/workflows/bandit.yml)

## Features

### Unified Telegram Hunting
Not quite yet lol. While you can leverage both scripts at the same time, the goal is the have one launch script, and have access to a dyanmic number of x-crawler instances inside the webUI. Allowing for parsing multiple tailored campaigns.

### Multilingual Search with Google Translate
With **Google Translation** integration, users can search for messages in multiple languages simultaneously. X-THing automatically translates search queries into the selected languages and displays unique and total matches.

### UI Enhancements
The search UI now leverages ellipses pagination for smoother navigation.

### Debug Info
While disabled by default, `x-thing.py` has logging in place for some background task data. Comment out the logging near the start of the script and update the main function to True.

### Modular Codebase
The goal is to try and keep things pretty modular so they're easy to maintain/customize.

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
