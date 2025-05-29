import os
import asyncio
import discord
from discord.ext import commands
from datetime import datetime
import pytz
import traceback

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix = "/", intents = intents)
token = "DISCORD_BOT_TOKEN"  # Replace with your actual bot token

def get_time():
    tz = pytz.timezone('Asia/Taipei')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# 當機器人完成啟動時    
@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    print(f"[{get_time()}] 載入 {len(slash)} 個斜線指令")

# 載入指令程式檔案
@bot.tree.command(name="load", description="Load a cog")
async def load(ctx: discord.Interaction, extension: str):
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.response.send_message(f"Loaded {extension} done.")
        print(f'[{get_time()}] Loaded {extension}')
    except Exception as e:
        await ctx.response.send_message(f"Error: {e}")
        print(f'[{get_time()}] {traceback.format_exc()}')

# 卸載指令檔案
@bot.tree.command(name="unload", description="Unload a cog")
async def unload(ctx: discord.Interaction, extension: str):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.response.send_message(f"Unloaded {extension} done.")
        print(f'[{get_time()}] Unloaded {extension}')
    except Exception as e:
        await ctx.response.send_message(f"Error: {e}")
        print(f'[{get_time()}] {traceback.format_exc()}')

# 重新載入程式檔案
@bot.tree.command(name="reload", description="Reload a cog")
async def reload(ctx: discord.Interaction, extension: str):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.response.send_message(f"ReLoaded {extension} done.")
        print(f'[{get_time()}] Reloaded {extension}')
    except Exception as e:
        await ctx.response.send_message(f"Error: {e}")
        print(f'[{get_time()}] {traceback.format_exc()}')

@bot.tree.command(name="list", description="List all cogs")
async def list(ctx: discord.Interaction):
    slash = await bot.tree.sync()
    slash = [f"{i.name} - {i.description}" for i in slash]
    if not slash: 
        slash = ["No cogs loaded."]
    # print("\n".join(slash))
    try:
        await ctx.response.send_message("\n".join(slash))
    except Exception as a:
        await ctx.response.send_message(a)
        print(f'[{get_time()}] ERROR: {a}')

@bot.tree.command(name="aloha", description="greets you")
async def aloha(ctx: discord.Interaction):
    await ctx.response.send_message("Aloha!")

# 一開始bot開機需載入全部程式檔案
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

# 確定執行此py檔才會執行
if __name__ == "__main__":
    asyncio.run(main())