import discord
import os
import csv
import asyncio
import pandas as pd
from datetime import datetime
from discord.ext import commands

# Load environment variables directly (from GitHub Secrets)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

# Create intents and enable the necessary ones
intents = discord.Intents.default()
intents.members = True  # Required for fetching user data to send DMs

# Initialize the Discord client with commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Data files
CSV_FILE_PATH = './scraper/bed_data.csv'
PREVIOUS_DATA_FILE = './scraper/previous_bed_data.csv'

# Dictionary to store user preferences
user_preferences = {}

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

# Function to compare bed data based on user preferences
def compare_bed_data(today_data, yesterday_data, user_gender, user_service):
    if today_data.empty or yesterday_data.empty:
        return None

    # Merge today's and yesterday's data on 'Name' and 'Purpose' to compare corresponding wards
    merged_data = pd.merge(today_data, yesterday_data, on=['Name', 'Purpose'], suffixes=('_today', '_yesterday'))

    # Filter based on user preferences
    if user_gender != 'All':
        merged_data = merged_data[merged_data['Sex_today'] == user_gender]

    if user_service != 'All':
        merged_data = merged_data[merged_data['Purpose_today'] == user_service]

    # Check where the number of beds has changed
    changes = merged_data[merged_data['Number of Beds_today'] != merged_data['Number of Beds_yesterday']]
    
    return changes

# Function to send a Discord DM for each change separately
async def send_discord_dm(user, changes):
    if changes is not None and not changes.empty:
        for index, row in changes.iterrows():
            message = (f"Hospital bed availability has changed:\n"
                       f"- Ward: {row['Name']} ({row['Purpose_today']})\n"
                       f"  Beds: {row['Number of Beds_yesterday']} -> {row['Number of Beds_today']}")
            await user.send(message)
    else:
        await user.send("No changes today.")

# Command to set preferences for gender
@bot.command(name='set_gender')
async def set_gender(ctx):
    user = ctx.message.author
    await user.send("Please choose a gender filter: `Male`, `Female`, `All`")

    def check(m):
        return m.author == user and m.content in ['Male', 'Female', 'All']

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        user_preferences['gender'] = msg.content
        await user.send(f"Gender filter set to: {msg.content}")
    except asyncio.TimeoutError:
        await user.send("No selection was made.")

# Command to set preferences for service type
@bot.command(name='set_service')
async def set_service(ctx):
    user = ctx.message.author
    await user.send("Please choose a service type filter: `Acute/PICU`, `PDU`, `Rehab`, `All`")

    def check(m):
        return m.author == user and m.content in ['Acute/PICU', 'PDU', 'Rehab', 'All']

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        user_preferences['service'] = msg.content
        await user.send(f"Service type filter set to: {msg.content}")
    except asyncio.TimeoutError:
        await user.send("No selection was made.")

# Command to start the notification process
@bot.command(name='start_notifications')
async def start_notifications(ctx):
    user = ctx.message.author

    # Get today's and yesterday's date
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    # Load today's and yesterday's data
    today_data, yesterday_data = load_data(CSV_FILE_PATH, today, yesterday)

    if today_data is not None and yesterday_data is not None:
        # Use user preferences to filter changes
        gender_pref = user_preferences.get('gender', 'All')
        service_pref = user_preferences.get('service', 'All')
        changes = compare_bed_data(today_data, yesterday_data, gender_pref, service_pref)

        # Send DMs based on preferences
        await send_discord_dm(user, changes)

        # Save today's data as the previous data for future runs
        today_data.to_csv(PREVIOUS_DATA_FILE, index=False)
        print("Previous data file updated with today's data.")
    else:
        await user.send("No data available for comparison.")

# Bot event when it's ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Run the bot
bot.run(DISCORD_TOKEN)
