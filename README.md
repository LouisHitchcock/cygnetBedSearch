
# Cygnet Bed Tracker

[![Build Status](https://github.com/louishitchcock/cygnetBedSearch/actions/workflows/scrape_beds.yml/badge.svg)](https://github.com/louishitchcock/cygnetBedSearch/actions)

This project scrapes bed availability data from the Cygnet Group's bed placement search website and sends daily Discord notifications with bed availability changes. The script compares the bed availability data between today and the previous day, and if changes are detected, it sends a message to the user. Additionally, the bot sends a daily summary message with or without changes.

## Features
- **Daily Bed Availability Scraper**: Scrapes the Cygnet Group bed search website to collect bed availability data.
- **Discord Notifications**: Sends a daily summary message to a user on Discord, indicating bed availability changes between today and the previous day.
- **Data Comparison**: Compares bed availability data (e.g., `Name`, `Sex`, `Number of Beds`, and `Purpose`) for each ward and alerts users if there are any changes.
- **Friendly Message Format**: Provides a message in the format:
  
  ```
  Hey! Here is the Bed Availability for Today (*DD-MM-YYYY*) -
  - Ward: <Ward Name> (<Purpose>)
    Beds: <Yesterday's Beds> -> <Today's Beds>
  =======================================
  ```

## Setup

### Prerequisites

- A **Discord bot** token (you can create a bot at [Discord Developer Portal](https://discord.com/developers/applications)).
- Python 3.x installed.
- Required libraries: `requests`, `beautifulsoup4`, `pandas`, `discord.py`
- A **GitHub repository** to run this workflow using **GitHub Actions**.

### Clone the Repository

```bash
git clone https://github.com/LouisHitchcock/cygnetBedSearch.git
cd cygnetBedSearch
```

### Install Dependencies

You can install the required Python dependencies by running:

```bash
pip install -r requirements.txt
```

Alternatively, if you want to install dependencies manually:

```bash
pip install requests beautifulsoup4 discord.py pandas
```

### GitHub Secrets Configuration

To send messages via Discord, you need to add the following secrets to your GitHub repository:

1. **DISCORD_TOKEN**: The bot token for your Discord bot.
2. **USER_ID**: Your Discord user ID to receive messages.

You can add these by going to **Settings** > **Secrets and Variables** > **Actions** > **New repository secret**.

### Setting Up the GitHub Actions Workflow

This repository uses a GitHub Actions workflow to automatically scrape and send Discord notifications daily.

1. Open `.github/workflows/scrape_beds.yml`.
2. Make sure the workflow runs at 10 AM every day by scheduling with cron:

   ```yaml
   on:
     schedule:
       - cron: "0 10 * * *"
   ```

### File Structure

```bash
cygnetBedSearch/
│
├── scraper/
│   ├── bed_data.csv            # Stores scraped bed data
│   ├── previous_bed_data.csv   # Stores yesterday's bed data for comparison
│   └── scrape_beds.py          # Scraper script to collect bed data
├── bot_script.py               # Bot script to send Discord notifications
├── .github/
│   └── workflows/
│       └── scrape_beds.yml     # GitHub Actions workflow file
└── README.md                   # Project README
```

## How It Works

1. **Scraping Bed Data**: The `scrape_beds.py` script runs daily to scrape bed availability data from the Cygnet Group's website.
2. **Data Comparison**: The bot compares today’s bed data with yesterday's and checks if there are any changes.
3. **Daily Discord Message**: The bot sends a daily message, either listing bed availability changes or indicating that there are no changes.
4. **Notification Format**: The message format includes the current date (`DD-MM-YYYY`) and lists changes for each ward in a user-friendly format.

## Running Locally

If you want to test the scraper and bot locally:

1. **Run the scraper**:
   ```bash
   python ./scraper/scrape_beds.py
   ```

2. **Run the Discord bot**:
   ```bash
   python bot_script.py
   ```

This will scrape data and send a notification to the specified Discord user.

## Example Discord Message

If there are changes in bed availability:

```
Hey! Here is the Bed Availability for Today (*18-09-2024*) -
- Ward: Cygnet Hospital Bury (PDU)
  Beds: 2 -> 1
- Ward: Cygnet Appletree (Acute/PICU)
  Beds: 2 -> 3
=======================================
```

If there are no changes:

```
Hey! Here is the Bed Availability for Today (*18-09-2024*) -
No changes today.
=======================================
```

## Contributing

Feel free to open an issue or submit a pull request for any bugs, improvements, or new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
