import discord
import os
import csv
import asyncio
from datetime import datetime

# Load environment variables directly (from GitHub Secrets)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

# Create intents and enable the necessary ones
intents = discord.Intents.default()
intents.members = True  # Required for fetching user data to send DMs

# Initialize the Discord client with intents
client = discord.Client(intents=intents)

CSV_FILE_PATH = './scraper/bed_data.csv'
PREVIOUS_DATA_FILE = './scraper/previous_bed_data.csv'

# Function to read the most recent day's data from CSV
def read_most_recent_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return None
    
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        if rows:
            return rows[-1]  # Return the last row (most recent entry)
        return None

# Function to compare current and previous bed data
def compare_bed_data(current_data, previous_data):
    if not current_data or not previous_data:
        return None  # No data to compare

    changes = []
    if current_data['Number of Beds'] != previous_data['Number of Beds']:
        changes.append({
            'ward': current_data['Name'],
            'purpose': current_data['Purpose'],
            'old_beds': previous_data['Number of Beds'],
            'new_beds': current_data['Number of Beds']
        })
    return changes

# Function to send a Discord DM
async def send_discord_dm(user, changes):
    if changes:
        message = "Hospital bed availability has changed!\n"
        for change in changes:
            message += (f"- Ward: {change['ward']} ({change['purpose']})\n"
                        f"  Beds: {change['old_beds']} -> {change['new_beds']}\n")
        await user.send(message)
    else:
        # Send a message indicating no changes
        await user.send("No changes today.")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Read today's data and previous day's data
    current_bed_data = read_most_recent_data(CSV_FILE_PATH)
    previous_bed_data = read_most_recent_data(PREVIOUS_DATA_FILE)

    if current_bed_data:
        print(f"Today's data: {current_bed_data}")
    if previous_bed_data:
        print(f"Yesterday's data: {previous_bed_data}")

    # Compare bed data and check for changes
    changes = compare_bed_data(current_bed_data, previous_bed_data)
    
    try:
        # Fetch the user to send a DM
        user = await client.fetch_user(USER_ID)
        
        # Send DM to the user whether there are changes or not
        await send_discord_dm(user, changes)

        # Save today's data as the previous data for future runs
        with open(PREVIOUS_DATA_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=current_bed_data.keys())
            writer.writeheader()
            writer.writerow(current_bed_data)
        
        print("Previous data file updated with today's data.")
    except discord.HTTPException as e:
        print(f"Failed to send DM: {e}")

    # Close the bot once the job is complete
    await client.close()

# This is the recommended method to run an asyncio application in Python 3.7+
if __name__ == "__main__":
    asyncio.run(client.start(DISCORD_TOKEN))
