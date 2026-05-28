import discord
import os
import asyncio
import httpx
from datetime import datetime, timedelta

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
API_URL = os.getenv("BED_API_URL", "http://localhost:8787")
API_TOKEN = os.getenv("BED_API_TOKEN", "")
STATUS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "DiscordBotStatus.txt",
)

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


def is_bot_enabled():
    if not os.path.exists(STATUS_FILE):
        return True
    with open(STATUS_FILE, "r") as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[1].strip().upper() == "Y"
    return True


async def get_changes_from_api(date_str: str):
    url = f"{API_URL}/api/data/changes?date={date_str}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()


async def send_discord_dm(user, changes, today):
    message = f"Hey! Here is the Bed Availability for Today (*{today}*) - \n"

    if changes and len(changes) > 0:
        for c in changes:
            message += (
                f"- Ward: {c['name']} ({c['purpose']})\n"
                f"  Beds: {c['beds_yesterday']} -> {c['beds_today']}\n"
            )
    else:
        message += "No changes today.\n"

    message += "======================================="
    await user.send(message)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    if not is_bot_enabled():
        print("Bot is disabled according to DiscordBotStatus.txt. Exiting.")
        await client.close()
        return

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        result = await get_changes_from_api(today)
        changes = result.get("changes", [])

        user = await client.fetch_user(USER_ID)
        await send_discord_dm(user, changes, today)
        print("Discord DM sent successfully.")
    except Exception as e:
        print(f"Failed to fetch changes or send DM: {e}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(client.start(DISCORD_TOKEN))
