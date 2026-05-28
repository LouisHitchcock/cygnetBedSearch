# Cygnet Bed Tracker

[![Build Status](https://github.com/louishitchcock/cygnetBedSearch/actions/workflows/scrape_beds.yml/badge.svg)](https://github.com/louishitchcock/cygnetBedSearch/actions)

Scrapes bed availability data from the Cygnet Group website and stores it in Cloudflare D1. Sends daily Discord notifications when bed counts change.

## Architecture

```
Cygnet Website --> Scraper (Playwright) --> Cloudflare Worker API --> D1 Database
                                                      |
                                                      +--> Website (index.html)
                                                      +--> Discord Bot
```

## Tech Stack

- **Data Store**: Cloudflare D1 (SQLite-compatible serverless DB)
- **API**: Cloudflare Worker (TypeScript)
- **Scraper**: Python (Playwright)
- **Notifications**: Discord bot (discord.py)
- **CI/CD**: GitHub Actions
- **Website**: Static HTML + Chart.js (fetches from the Worker API)

## Setup

### 1. Cloudflare Worker & D1

```bash
# Install wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Navigate to the worker directory
cd worker

# Install dependencies
npm install

# Create the D1 database
wrangler d1 create cygnet-bed-search-db
# -> Copy the database_id output, paste it into wrangler.toml

# Apply the schema
wrangler d1 execute cygnet-bed-search-db --file=./schema.sql

# Set the API token secret (generate a strong random string)
wrangler secret put API_TOKEN

# Deploy the worker
npm run deploy
```

Once deployed, note the worker URL (e.g. `https://cygnet-bed-search-worker.YOUR_ACCOUNT.workers.dev`).

### 2. Migrate Existing Data

```bash
export BED_API_URL="https://cygnet-bed-search-worker.YOUR_ACCOUNT.workers.dev"
export BED_API_TOKEN="the-token-you-set"
python migrate_csv_to_d1.py
```

### 3. GitHub Secrets

Add these secrets to your GitHub repo:

| Secret | Value |
|--------|-------|
| `BED_API_URL` | Your Worker URL |
| `BED_API_TOKEN` | The API token you set |
| `DISCORD_TOKEN` | Your Discord bot token |
| `USER_ID` | Your Discord user ID |

### 4. Website

Update the `API_BASE` variable in `index.html` to point to your Worker URL, or serve the site on Cloudflare Pages and set it via an environment variable.

## Project Structure

```
cygnetBedSearch/
├── worker/
│   ├── src/index.ts          # Cloudflare Worker API
│   ├── schema.sql            # D1 database schema
│   ├── wrangler.toml          # Wrangler config
│   └── package.json
├── scraper/
│   ├── scrape_beds.py       # Scraper (sends to API)
│   ├── bot_script.py        # Discord bot (queries API)
│   ├── api_client.py        # Shared API client
│   └── bed_data.csv          # Historical data (read-only after migration)
├── migrate_csv_to_d1.py   # One-time migration script
├── index.html             # Website
├── style.css
├── requirements.txt
└── .github/workflows/scrape_beds.yml
```

## Running Locally

```bash
# Start the Worker in dev mode
cd worker && npm run dev &

# Run the scraper (it will POST to localhost:8787)
export BED_API_URL="http://localhost:8787"
export BED_API_TOKEN="your-token"
python scraper/scrape_beds.py

# Run the Discord bot
export DISCORD_TOKEN="..."
export USER_ID="..."
python scraper/bot_script.py
```
