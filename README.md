## Overview

**GamerTagIDGrabber** is a Discord bot written in Python that performs bidirectional lookups between user-facing handles and account IDs on both Xbox Live and PlayStation Network. With simple commands, you can:

* Convert an Xbox Gamertag → XBOX User ID (XUID)
* Convert an XBOX User ID (XUID) → Xbox Gamertag
* Convert a PSN Gamertag → PSN Gamertag ID (PSNID)
* Convert a PSN Gamertag ID (PSNID) → PSN Gamertag

## Prerequisites

* **Python 3.11+**
* A **Discord Bot Token**
* An **OpenXBL API Token**
* An **NPSSO Code**

### OpenXBL
To get open XBL token see the instructions on this website: https://xbl.io/

### NPSSO COOKIE
For NPSSO cookie follow the instructions from this repo README.md: https://github.com/isFakeAccount/psnawp

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/isFakeAccount/GamerTagIDGrabber.git
   cd GamerTagIDGrabber
   ```

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Copy & edit the example config**

   ```bash
   cp .env.example .env
   ```

   Populate `.env` with your credentials (see below).

## Configuration

In your project root, create or update `.env` with:

```dotenv
DISCORD_TOKEN=<your_discord_bot_token>
OPENXBL_API=<your_openxbl_api_token>
NPSSO_CODE=<your_npsso_code>
```

## Usage

1. Activate your virtual environment:

   ```bash
   source .venv/bin/activate
   ```
2. Start the bot:

   ```bash
   python main.py
   ```

Once online, use these commands in any Discord channel the bot can access:

| Command                                          | Description                                                                |
| ------------------------------------------------ | -------------------------------------------------------------------------- |
| `/xbox get_xuid <XBOX Gamertag>`                 | Returns the XUID for the given Gamertag                                    |
| `/xbox get_gamertag <XBOX User ID>`              | Returns the Gamertag for the given XUID                                    |
| `/xbox_legacy get_xuid <XBOX Gamertag>`          | Returns the XUID for the given Gamertag using the legacy Xbox API          |
| `/playstation get_psnid <PlayStation Online ID>` | Returns the NPSSO (account) ID for the given PSN Online ID                 |
| `/playstation get_gamertag <PSN Account ID>`     | Returns the PSN Online ID for the given account ID                         |
| `/playstation set_npsso_cookie <npsso_cookie>`   | Sets the NPSSO cookie to authorize subsequent PSN API requests (no output) |
