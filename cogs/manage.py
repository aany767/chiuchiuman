# 此檔案請修改 12, 13, 23行 #

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import pytz
from datetime import datetime
import json
import traceback

cart_file = 'CART_FILE_PATH'  # Replace with the actual path to your cart file
r_admin = 'R_ADMIN_ROLE_FILE_PATH'  # Replace with the actual path to your admin role file

def get_cart():
    with open(cart_file, 'r') as f:
        data = json.load(f)
    return data

class link_view(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__()
        self.add_item(discord.ui.Button(emoji='🔗', url="N8N_URL", style=discord.ButtonStyle.link))

class manage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="delete_order", description="delete the order")
    async def delete_order(self, interaction: discord.Interaction, order_number: str):
        role = json.load(open(r_admin, 'r'))[str(interaction.guild_id)]
        if role in [role.id for role in interaction.user.roles]:
            data = get_cart()
            guild_id_str = str(interaction.guild_id)
            if guild_id_str not in data:
                await interaction.response.send_message(content='No order has been set.')
            else:
                if not data[guild_id_str]:
                    await interaction.response.send_message(content='No order has been set.')
                    
                else:
                    del data[guild_id_str][order_number]
                    with open(cart_file, 'w') as f:
                        json.dump(data, f, indent=4)
                    await interaction.response.send_message(content='Order deleted.')
        else:
            await interaction.response.send_message(content='You do not have permission to delete the order.')
        
    @app_commands.command(name='view_orders', description='get link to view the orders')
    async def view_order(self, interaction: discord.Interaction):
        role = json.load(open(r_admin, 'r'))[str(interaction.guild_id)]
        if role not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(content='You do not have permission to view the orders.')
            return
        else:
            try:
                await interaction.response.send_message(view=link_view())
            except:
                print(traceback.format_exc())


async def setup(bot):   
    await bot.add_cog(manage(bot))