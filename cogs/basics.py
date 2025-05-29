import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import pytz
from datetime import datetime

def get_time():
    tz = pytz.timezone('Asia/Taipei')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# 定義名為 Main 的 Cog
class basics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @app_commands.command(name="kickuser", description="kick someone u hate")
    async def kickuser(self, interaction: discord.Interaction, member: discord.Member, *, reason: str):
        try:
            if interaction.user.guild_permissions.kick_members:
                if member.guild_permissions.kick_members:
                    await interaction.response.send_message(f'無法踢出{member.mention}！')
                else: 
                    await interaction.response.send_message(f'{member.mention}你因為{reason}在30秒內將被踢出😡')
                    await asyncio.sleep(30)
                    await member.kick(reason=reason)
                    await interaction.followup.send(f'已踢出{member.mention}')
            else:
                await interaction.response.send_message(f'你沒有權限踢出{member.mention}')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @app_commands.command(name="change_activity", description="set activity")
    async def change_activity(self, interaction: discord.Interaction, activity: str):
        try:
            await interaction.response.send_message(f'現在開始玩 {activity}')
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=activity, type=3))
            print(f'[{get_time()}] Bot activity changed to {activity}')
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}')

    @app_commands.command(name="what_time", description="tells you the time")
    async def what_time(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'現在時間是 {get_time()}')

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        
# Cog 載入 Bot 中
async def setup(bot: commands.Bot): 
    await bot.add_cog(basics(bot))
