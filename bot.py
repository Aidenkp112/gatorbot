import discord
import os
import json
import threading
import traceback
from dotenv import load_dotenv
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask

print("BOT STARTING...")

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
print("TOKEN LOADED:", TOKEN is not None)

IMAGE_URL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/86caa92d-e1bf-4f41-99cb-c554002b134c/dlyt1h4-7659f17b-4bff-4b62-b52b-7a6aaf5d241f.png/v1/fit/w_460,h_469,q_70,strp/gator_by_aidenkp11_dlyt1h4-375w-2x.jpg"

# ---------------- WEB SERVER (REQUIRED FOR RENDER) ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()


# ---------------- DISCORD BOT ----------------

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

scheduler = AsyncIOScheduler()

CHANNEL_FILE = "channels.json"
TIME_FILE = "times.json"


# ---------------- SAFE JSON ----------------

def load_json(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


# ---------------- SEND IMAGE ----------------

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

    async def job():
        await send_image_to_guild(guild_id)

    scheduler.add_job(
        lambda: client.loop.create_task(job()),
        "cron",
        hour=hour,
        minute=minute,
        id=job_id
    )


def restore_schedules():
    times = load_json(TIME_FILE)

    for guild_id, t in times.items():
        schedule_guild(guild_id, t["hour"], t["minute"])


# ---------------- READY ----------------

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    try:
        await tree.sync()
        print("Commands synced")
    except Exception as e:
        print("SYNC ERROR:", e)

    scheduler.start()
    restore_schedules()

    print("Bot fully ready")


# ---------------- COMMANDS ----------------

@tree.command(name="setchannel", description="Set image channel")
async def setchannel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("nope!", ephemeral=True)
        return

    channels = load_json(CHANNEL_FILE)
    channels[str(interaction.guild.id)] = interaction.channel.id
    save_json(CHANNEL_FILE, channels)

    await interaction.response.send_message("channel set", ephemeral=True)


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
        f"time set to {hour:02d}:{minute:02d}",
        ephemeral=True
    )


@tree.command(name="sendimage", description="Force send image now")
async def sendimage(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("nope!", ephemeral=True)
        return

    await interaction.channel.send(IMAGE_URL)
    await interaction.response.send_message("gator sent", ephemeral=True)


# ---------------- RUN BOT ----------------

try:
    client.run(TOKEN)
except Exception:
    traceback.print_exc()
