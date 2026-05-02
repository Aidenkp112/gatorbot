import discord
from discord.ext import commands, tasks
import os
import asyncio
from flask import Flask
from threading import Thread

# ========================
# KEEP-ALIVE WEB SERVER
# ========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ========================
# DISCORD BOT SETUP
# ========================
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# SAFE STARTUP (ANTI-RATE LIMIT)
# ========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ========================
# COMMANDS
# ========================

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command()
async def forcepic(ctx):
    await ctx.send("https://picsum.photos/300")

# ========================
# BACKGROUND TASK (SAFE)
# ========================
@tasks.loop(minutes=10)  # NOT spammy
async def periodic_task():
    print("Running scheduled task...")

@periodic_task.before_loop
async def before_task():
    await bot.wait_until_ready()

# ========================
# MAIN START (CRITICAL FIX)
# ========================
async def main():
    keep_alive()  # start web server

    await asyncio.sleep(15)  
    # ⬆️ prevents instant Cloudflare 1015

    if not TOKEN:
        print("❌ TOKEN NOT FOUND")
        return

    try:
        await bot.start(TOKEN)
    except discord.HTTPException as e:
        print(f"❌ HTTP ERROR: {e}")
        await asyncio.sleep(60)  # wait if rate limited

# ========================
# RUN
# ========================
print("🚀 BOT STARTING...")

try:
    asyncio.run(main())
except Exception as e:
    print(f"CRASH: {e}")
