import discord
import os
import csv
import asyncio
import pandas as pd
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
STATUS_FILE = './DiscordBotStatus.txt'  # File that controls bot status

# Function to load today's and yesterday's data from CSV
def load_data(file_path, today, yesterday):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return None, None

    data = pd.read_csv(file_path)
    
    # Filter the data for today's and yesterday's dates
    today_data = data[data['Date'] == today]
    yesterday_data = data[data['Date'] == yesterday]

    return today_data, yesterday_data

# Function to compare bed data
def compare_bed_data(today_data, yesterday_data):
    if today_data.empty or yesterday_data.empty:
        return None

    # Merge today's and yesterday's data on 'Name' and 'Purpose' to compare corresponding wards
    merged_data = pd.merge(today_data, yesterday_data, on=['Name', 'Purpose'], suffixes=('_today', '_yesterday'))

    # Check where the number of beds has changed
    changes = merged_data[merged_data['Number of Beds_today'] != merged_data['Number of Beds_yesterday']]
    
    return changes

# Function to send a Discord DM
async def send_discord_dm(user, changes, today):
    message = f"Hey! Here is the Bed Availability for Today (*{today}*) - \n"

    if changes is not None and not changes.empty:
        for index, row in changes.iterrows():
            message += (f"- Ward: {row['Name']} ({row['Purpose']})\n"
                        f"  Beds: {row['Number of Beds_yesterday']} -> {row['Number of Beds_today']}\n")
    else:
        message += "No changes today.\n"

    # End the message with a line separator
    message += "======================================="

    # Send the formatted message
    await user.send(message)

# Function to check if the bot is enabled or disabled
def is_bot_enabled():
    if not os.path.exists(STATUS_FILE):
        print(f"{STATUS_FILE} not found! Defaulting to bot enabled.")
        return True  # If the status file doesn't exist, we default to enabling the bot.

    with open(STATUS_FILE, 'r') as file:
        lines = file.readlines()

        # Expecting the format:
        # Is the bot Enabled: Y/N
        # Y (or N)
        if len(lines) >= 2:
            status = lines[1].strip()
            if status.upper() == 'Y':
                return True
            elif status.upper() == 'N':
                return False
            else:
                print(f"Unrecognized status: {status}. Defaulting to bot enabled.")
                return True
        else:
            print("Invalid status file format. Defaulting to bot enabled.")
            return True

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Check if the bot is enabled
    if not is_bot_enabled():
        print("Bot is disabled according to DiscordBotStatus.txt. Exiting.")
        await client.close()  # Exit the bot if it's disabled
        return

    # Get today's and yesterday's date
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    # Load today's and yesterday's data
    today_data, yesterday_data = load_data(CSV_FILE_PATH, today, yesterday)

    if today_data is not None and yesterday_data is not None:
        print(f"Today's data:\n{today_data}")
        print(f"Yesterday's data:\n{yesterday_data}")

        # Compare bed data and check for changes
        changes = compare_bed_data(today_data, yesterday_data)
        
        try:
            # Fetch the user to send a DM
            user = await client.fetch_user(USER_ID)
            
            # Send DM to the user with formatted message
            await send_discord_dm(user, changes, today)

            # Save today's data as the previous data for future runs
            today_data.to_csv(PREVIOUS_DATA_FILE, index=False)
            print("Previous data file updated with today's data.")
        except discord.HTTPException as e:
            print(f"Failed to send DM: {e}")
    else:
        print("No data available for comparison.")

    # Close the bot once the job is complete
    await client.close()

# This is the recommended method to run an asyncio application in Python 3.7+
if __name__ == "__main__":
    asyncio.run(client.start(DISCORD_TOKEN))
