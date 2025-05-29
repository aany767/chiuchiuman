import discord
from discord.ext import commands
import logging

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.basicConfig(
            filename='dcbot_errors.log', 
            level=logging.ERROR, 
            format='[%(asctime)s] - %(levelname)s - %(message)s', 
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print("Event cog is ready!")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logging.error(f"Error occurred during {event}: {args}, {kwargs}")

async def setup(bot):
    await bot.add_cog(Event(bot))
