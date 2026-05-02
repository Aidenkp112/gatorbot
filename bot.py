import discord
from discord.ext import commands, tasks
import os
import asyncio
import logging

# ========================
# LOGGING (IMPORTANT FOR RENDER)
# ========================
logging.basicConfig(level=logging.INFO)

# ========================
# BOT SETUP
# ========================
TOKEN = os.getenv("DISCORD_TOKEN")  # safer naming

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# EVENTS
# ========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_disconnect():
    print("⚠️ Bot disconnected from Discord")

@bot.event
async def on_resumed():
    print("🔄 Bot session resumed")

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
@tasks.loop(minutes=10)
async def periodic_task():
    print("📡 Running scheduled task...")

@periodic_task.before_loop
async def before_task():
    await bot.wait_until_ready()

# ========================
# MAIN START (PROPER WAY)
# ========================
async def main():
    if not TOKEN:
        raise RuntimeError("❌ DISCORD_TOKEN not found in environment variables")

    periodic_task.start()

    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid token")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")

# ========================
# ENTRY POINT
# ========================
if __name__ == "__main__":
    print("🚀 BOT STARTING...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Bot shutting down")
