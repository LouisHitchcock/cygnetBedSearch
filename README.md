# Cygnet Bed Tracker

[![Build Status](https://github.com/louishitchcock/cygnetBedSearch/actions/workflows/scrape_beds.yml/badge.svg)](https://github.com/louishitchcock/cygnetBedSearch/actions)

Scrapes bed availability data from the Cygnet Group website and stores it in Cloudflare D1 for reliable, scalable data storage. Sends daily Discord notifications when bed counts change.

## Architecture

```
Cygnet Website --> Scraper (Playwright) --> Cloudflare Worker API --> D1 Database
                                                      |
                                                      +--> Website (index.html)
                                                      +--> Discord Bot
```

## Tech Stack

- **Data Store**: Cloudflare D1 (SQLite-compatible serverless SQL DB)
- **API**: Cloudflare Worker (TypeScript)
- **Scraper**: Python + Playwright
- **Notifications**: Discord bot (discord.py)
- **CI/CD**: GitHub Actions
- **Frontend**: Static HTML + Chart.js

## Quick Start (Already Deployed)

The Worker is already deployed at:
`https://cygnet-bed-search-worker.fpvgate-analytics.workers.dev`

### API Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|:---:|
| `GET` | `/api/data/all` | All historical data | No |
| `GET` | `/api/data/today` | Latest day's snapshot | No |
| `GET` | `/api/data/range?from=YYYY-MM-DD&to=YYYY-MM-DD` | Date range | No |
| `GET` | `/api/data/changes?date=YYYY-MM-DD` | Changes vs previous day | No |
| `POST` | `/api/data` | Insert scrape results | Yes |
| `POST` | `/api/migrate` | Bulk insert (migration) | Yes |

## Setup (from scratch)

### Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- Python 3.10+
- A Cloudflare account

### 1. Deploy the Worker

```bash
# Install dependencies and deploy
cd worker
npm install

# Login to Cloudflare
npx wrangler login

# Create the D1 database
npx wrangler d1 create cygnet-bed-search-db
# -> Copy the database_id, paste into wrangler.toml

# Apply the schema
npx wrangler d1 execute cygnet-bed-search-db --remote --file=./schema.sql

# Set a secret API token
npx wrangler secret put API_TOKEN

# Deploy
npx wrangler deploy
```

### 2. Migrate Existing CSV Data

```bash
pip install -r requirements.txt
export BED_API_URL="https://your-worker.workers.dev/api/migrate"
export BED_API_TOKEN="your-secret-token"
python migrate_csv_to_d1.py
```

### 3. GitHub Repository Secrets

Add these secrets to your GitHub repo (**Settings > Secrets and Variables > Actions**):

| Secret | Description |
|--------|-------------|
| `BED_API_URL` | Your Worker URL (e.g. `https://cygnet-bed-search-worker.fpvgate-analytics.workers.dev`) |
| `BED_API_TOKEN` | The API_TOKEN secret you set on the Worker |
| `DISCORD_TOKEN` | Your Discord bot token |
| `USER_ID` | Your Discord user ID to receive DM notifications |

### 4. Run the Website

Open `index.html` in your browser. It fetches data from the Worker API via the `API_BASE` constant at the top of the script. The website is fully static and can be served from any static host (GitHub Pages, Cloudflare Pages, etc.).

## Project Structure

```
cygnetBedSearch/
├── worker/                      # Cloudflare Worker
│   ├── src/index.ts             # Worker API (TypeScript)
│   ├── schema.sql               # D1 table schema
│   ├── wrangler.toml            # Wrangler config
│   └── package.json
├── scraper/
│   ├── scrape_beds.py           # Playwright scraper (sends to API)
│   ├── bot_script.py            # Discord bot (queries API)
│   ├── api_client.py            # Shared HTTP client for the API
│   └── bed_data.csv             # Historical data backup (read-only)
├── migrate_csv_to_d1.py         # One-time migration script
├── index.html                   # Website
├── style.css                    # Website CSS
├── requirements.txt             # Python dependencies
└── .github/workflows/           # GitHub Actions CI
```

## Running Locally

```bash
# Start the Worker in dev mode
cd worker
npx wrangler dev

# In another terminal, run the scraper
export BED_API_URL="http://localhost:8787"
export BED_API_TOKEN="your-token"
python scraper/scrape_beds.py

# Run the Discord bot
export DISCORD_TOKEN="your-token"
export USER_ID="your-id"
export BED_API_URL="http://localhost:8787"
export BED_API_TOKEN="your-token"
python scraper/bot_script.py
```

## Example Discord Message

```
Hey! Here is the Bed Availability for Today (*2024-09-18*) -
- Ward: Cygnet Hospital Bury (PDU)
  Beds: 2 -> 1
- Ward: Cygnet Appletree (Acute/PICU)
  Beds: 2 -> 3
=======================================
```

## License

MIT
