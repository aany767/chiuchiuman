import discord
from discord.ext import commands
from discord import app_commands

class main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @app_commands.command(name="hello", description="Say hello World!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("hello, world!")

    @app_commands.command(name = 'add', description='簡單加法而已')
    async def add(self, interaction: discord.Interaction, a: int, b: int):
        await interaction.response.send_message(f"{a} + {b} = {a + b}")

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "hello":
            await message.channel.send("hello")

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(main(bot))
