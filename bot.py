import discord
import os
import json
from dotenv import load_dotenv
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
IMAGE_URL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/86caa92d-e1bf-4f41-99cb-c554002b134c/dlyt1h4-7659f17b-4bff-4b62-b52b-7a6aaf5d241f.png/v1/fit/w_460,h_469,q_70,strp/gator_by_aidenkp11_dlyt1h4-375w-2x.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NDY5IiwicGF0aCI6Ii9mLzg2Y2FhOTJkLWUxYmYtNGY0MS05OWNiLWM1NTQwMDJiMTM0Yy9kbHl0MWg0LTc2NTlmMTdiLTRiZmYtNGI2Mi1iNTJiLTdhNmFhZjVkMjQxZi5wbmciLCJ3aWR0aCI6Ijw9NDYwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.f_QCdPch84JHGyExzTVUYw3MGDv1qQcl7tNWPuajetc"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

scheduler = AsyncIOScheduler()

CHANNEL_FILE = "channels.json"
TIME_FILE = "times.json"


# ---------------- FILE HELPERS ----------------

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


# ---------------- SEND FUNCTION ----------------

async def send_image_to_guild(guild_id):
    channels = load_json(CHANNEL_FILE)
    channel_id = channels.get(str(guild_id))

    if not channel_id:
        return

    channel = client.get_channel(int(channel_id))
    if channel:
        await channel.send(IMAGE_URL)


# ---------------- SCHEDULER ----------------

def schedule_guild(guild_id, hour, minute):
    job_id = f"job_{guild_id}"

    try:
        scheduler.remove_job(job_id)
    except:
        pass

    scheduler.add_job(
        lambda: client.loop.create_task(send_image_to_guild(guild_id)),
        "cron",
        hour=hour,
        minute=minute,
        id=job_id
    )


def restore_schedules():
    times = load_json(TIME_FILE)

    for guild_id, t in times.items():
        schedule_guild(guild_id, t["hour"], t["minute"])


# ---------------- BOT READY ----------------

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    await tree.sync()

    scheduler.start()
    restore_schedules()


# ---------------- COMMANDS ----------------

# 🔹 set channel
@tree.command(name="setchannel", description="Set image channel")
async def setchannel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("nope!", ephemeral=True)
        return

    channels = load_json(CHANNEL_FILE)
    channels[str(interaction.guild.id)] = interaction.channel.id
    save_json(CHANNEL_FILE, channels)

    await interaction.response.send_message("channel set", ephemeral=True)


# 🔹 set time
@tree.command(name="settime", description="Set daily image time")
@app_commands.describe(hour="0-23", minute="0-59")
async def settime(interaction: discord.Interaction, hour: int, minute: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("nope!", ephemeral=True)
        return

    times = load_json(TIME_FILE)
    times[str(interaction.guild.id)] = {"hour": hour, "minute": minute}
    save_json(TIME_FILE, times)

    schedule_guild(interaction.guild.id, hour, minute)

    await interaction.response.send_message(
        f"time set to {hour:02d}:{minute:02d}", ephemeral=True
    )


# 🔹 force send image
@tree.command(name="sendimage", description="Force send the image now")
async def sendimage(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("nope!", ephemeral=True)
        return

    await interaction.channel.send(IMAGE_URL)
    await interaction.response.send_message("gator sent", ephemeral=True)


# ---------------- RUN BOT ----------------

client.run(TOKEN)
