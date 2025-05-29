# 此檔案請修改第 12 行 #

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import pytz
from datetime import datetime
import json
import traceback

role_file = "R_ADMIN_ROLE_FILE_PATH"  # Replace with the actual path to your admin role file

class setrole(commands.Cog):
    @app_commands.command(name='set_role', description='set a role that repersents restaurant admins')
    @commands.has_permissions(administrator=True)
    async def set_role(self, interaction: discord.Interaction, role: discord.Role):
        interaction.response.defer(thinking=True)    
        guild_id_str = str(interaction.guild_id)
        with open(role_file, 'r') as f:
            data = json.load(f)
        
        if guild_id_str not in data:
            data[guild_id_str] = role.id
            
            with open(role_file, 'w') as f:
                json.dump(data, f)
            
            await interaction.response.send_message(f"Set {role.mention} as the restaurant admin role")
        else:
            data[guild_id_str] = role.id
            
            with open(role_file, 'w') as f:
                json.dump(data, f)
            
            await interaction.response.send_message(f"Updated {role.mention} as the restaurant admin role")
        
            print(traceback.format_exc())

    @app_commands.command(name='list_admin', description='list all restaurant admins')
    async def list_admin(self, interaction: discord.Interaction):
        with open(role_file, 'r') as f:
            data = json.load(f)
        if str(interaction.guild_id) not in data:
            await interaction.response.send_message("No role has been set as the restaurant admin role")
        else:
            gulid_id_str = str(interaction.guild_id)
            role_id = data[gulid_id_str]
            role = interaction.guild.get_role(role_id)
            l = [member.mention for member in role.members]
            embed = discord.Embed(title="Restaurant Admins", description="List of all restaurant admins with the role of " + role.mention, color=discord.Colour.from_rgb(111, 162, 242))
            embed.add_field(name='Members', value='\n\n'.join(l), inline=False)
            # embed.add_field(name='Role', value='\n\n'.join(role), inline=False)
            await interaction.response.send_message(embed=embed)
            

async def setup(bot):
    await bot.add_cog(setrole(bot))