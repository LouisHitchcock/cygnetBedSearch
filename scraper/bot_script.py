import discord
import os
import csv
import asyncio

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

# Function to read bed data from CSV
def read_bed_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return []
    
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to compare current and previous bed data
def compare_bed_data(current_data, previous_data):
    changes = []
    
    if not current_data or not previous_data:
        print("No current or previous data available for comparison.")
        return changes
    
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
    else:
        print("No changes detected, no message sent.")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Read current and previous bed data
    current_bed_data = read_bed_data(CSV_FILE_PATH)
    previous_bed_data = read_bed_data(PREVIOUS_DATA_FILE)

    # Compare bed data and check for changes
    changes = compare_bed_data(current_bed_data, previous_bed_data)
    
    if changes:
        # Send DM to the user if there are any changes
        try:
            await send_discord_dm(user, changes)
        except discord.HTTPException as e:
            print(f"Failed to send DM: {e}")
    
    # Save current bed data as the previous data for future runs
    with open(PREVIOUS_DATA_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=current_bed_data[0].keys())
        writer.writeheader()
        writer.writerows(current_bed_data)

    # Close the bot once the job is complete
    await client.close()

# This line ensures that the script works properly within an asyncio event loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start(DISCORD_TOKEN))
