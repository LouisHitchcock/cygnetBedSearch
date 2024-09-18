import discord
import os
import csv
from dotenv import load_dotenv

# Load environment variables from GitHub Actions
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

client = discord.Client()

CSV_FILE_PATH = './scraper/bed_data.csv'
PREVIOUS_DATA_FILE = './scraper/previous_bed_data.csv'

# Function to read bed data from CSV
def read_bed_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to compare current and previous bed data
def compare_bed_data(current_data, previous_data):
    changes = []
    for current_row in current_data:
        for previous_row in previous_data:
            if current_row['Name'] == previous_row['Name'] and current_row['Purpose'] == previous_row['Purpose']:
                if current_row['Number of Beds'] != previous_row['Number of Beds']:
                    changes.append({
                        'ward': current_row['Name'],
                        'purpose': current_row['Purpose'],
                        'old_beds': previous_row['Number of Beds'],
                        'new_beds': current_row['Number of Beds']
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

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Read current and previous bed data
    current_bed_data = read_bed_data(CSV_FILE_PATH)
    
    if os.path.exists(PREVIOUS_DATA_FILE):
        previous_bed_data = read_bed_data(PREVIOUS_DATA_FILE)
    else:
        previous_bed_data = []

    # Compare bed data and check for changes
    changes = compare_bed_data(current_bed_data, previous_bed_data)
    
    if changes:
        # Send DM to the user if there are any changes
        user = await client.fetch_user(USER_ID)
        await send_discord_dm(user, changes)

        # Save current bed data as the previous data for future runs
        with open(PREVIOUS_DATA_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=current_bed_data[0].keys())
            writer.writeheader()
            writer.writerows(current_bed_data)
    
    await client.close()

client.run(DISCORD_TOKEN)
