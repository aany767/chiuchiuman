# 此檔案請修改 12-14 行 #

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import pytz
from datetime import datetime
import json
import traceback
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

menu_file = "MENU_FILE_PATH"  # Replace with the actual path to your menu file
r_admin = "R_ADMIN_ROLE_FILE_PATH"  # Replace with the actual path to your admin role file
cogs_folder_path = "COGS_FOLDER_PATH"  # Replace with the actual path to your cogs folder

def make_menu(menu, guild_name):
    embed = discord.Embed(title=f"{guild_name}'s Menu", description=menu['description'], color=discord.Colour.from_rgb(111, 162, 242))
    items, prices = [], []
    for item in menu['items']:
        items.append(item)
        prices.append('$ ' + str(menu['items'][item]))
    embed.add_field(name='item', value='\n'.join(items), inline=True)
    embed.add_field(name='price', value='\n'.join(prices), inline=True)
    return embed

async def watch(interaction: discord.Interaction, seconds=180):
    event_handler = filechange_handler(
                    interaction,
                    interaction.guild_id,
                    patterns=[menu_file],
                    ignore_directories=True,
                    case_sensitive=False
                )
    observer = Observer()
    # Watch the directory containing the file
    observer.schedule(event_handler, path=cogs_folder_path, recursive=False)
    observer.start()

    try:
        await asyncio.sleep(seconds)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    finally:
        observer.stop()

class filechange_handler(PatternMatchingEventHandler):
    def __init__(self, interaction: discord.Interaction, guild_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.guild_id = guild_id
        

    def on_modified(self, event):
        asyncio.run_coroutine_threadsafe(self.update_interaction(), self.interaction.client.loop)

    async def update_interaction(self):
        updated_content = "The file has been updated!"
        try:
            data = json.load(open(menu_file, 'r'))
            embed = make_menu(data[str(self.guild_id)], self.interaction.guild.name)
            await self.interaction.edit_original_response(embed=embed)
        except Exception as e:
            print(traceback.format_exc())

class edit_view(discord.ui.View):
    def __init__(self, guild_id, i: discord.Interaction):
        super().__init__(timeout=600)
        self.guild_id = guild_id
        self.i = i

    async def on_timeout(self):
        try: 
            # print(type(self.i))
            await self.i.edit_original_response(content='Expired. Please enter the command again to edit the menu.', view=None)
            # self.clear_items()
        except Exception as e:
            print(traceback.format_exc())


    @discord.ui.button(label='Import Menu', style=discord.ButtonStyle.primary)
    async def import_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(import_modal(self.guild_id))
        except Exception as e:
            print(traceback.format_exc())

    @discord.ui.button(label='Edit Description', style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(desc_modal(self.guild_id))
        except Exception as e:
            print(traceback.format_exc())

    
class desc_modal(discord.ui.Modal, title='Edit Description'):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        
        with open(menu_file, 'r') as f:
            self.data = json.load(f)
        self.description = self.data[str(guild_id)]['description']
        self.description_input = discord.ui.TextInput(label='Description', placeholder='description', default=self.description, style=discord.TextStyle.long)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.data[str(self.guild_id)]['description'] = self.description_input.value
            with open(menu_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            embed = make_menu(self.data[str(self.guild_id)], interaction.guild.name)
            await interaction.response.edit_message(content='edited', embed=embed)
        except:
            print(traceback.format_exc())
            await interaction.response.edit_message(content='format Error')

class import_modal(discord.ui.Modal, title='Import Menu'):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        
        with open(menu_file, 'r') as f:
            self.data = json.load(f)
        self.menu_content = self.data[str(guild_id)]['items']
        if self.menu_content:
            self.menu_str = '\n'.join([f"{item}*{int(price)}" for item, price in self.menu_content.items()])

        self.import_menu = discord.ui.TextInput(label='Import Menu (use * between an item and price)', placeholder='item1*price1\nitem2*price2\n...', default=self.menu_str, style=discord.TextStyle.long)
        self.add_item(self.import_menu)

    async def on_submit(self, interaction: discord.Interaction):
        write = {}
        try:
            
            for item_price in self.import_menu.value.split('\n'):
                item, price = item_price.split('*')
                write[item.strip()] = int(price.strip())
            self.data[str(self.guild_id)]['items'] = write
            with open(menu_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            embed = make_menu(self.data[str(self.guild_id)], interaction.guild.name)
            await interaction.response.edit_message(content='edited', embed=embed)
        except:
            # print(traceback.format_exc())
            await interaction.response.edit_message(content='format Error')

class menuedit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='show_menu', description='show the menu')
    async def show_menu(self, interaction: discord.Interaction):
        with open(menu_file, 'r') as f:
            data = json.load(f)
        if str(interaction.guild_id) not in data:
            await interaction.response.send_message("No menu has been set")
        else:
            gulid_id_str = str(interaction.guild_id)
            menu = data[gulid_id_str]
            guild_name = interaction.guild.name
            embed = make_menu(menu, guild_name)
            await interaction.response.send_message(embed=embed)
            try:
                await watch(interaction)
                await interaction.edit_original_response(content='Expired', embed=None)
            except Exception as e:
                print(traceback.format_exc())

    @app_commands.command(name='edit_menu', description='edit the menu')
    async def edit_menu(self, interaction: discord.Interaction):
        role = json.load(open(r_admin, 'r'))[str(interaction.guild_id)]
        if role in [role.id for role in interaction.user.roles]:
            with open(menu_file, 'r') as f:
                data = json.load(f)
            if str(interaction.guild_id) not in data:
                await interaction.response.send_message(content='No menu has been set. Import a menu first.')
            else:
                gulid_id_str = str(interaction.guild_id)
                menu = data[gulid_id_str]
                guild_name = interaction.guild.name
                embed = make_menu(menu, guild_name)
                await interaction.response.send_message(embed=embed, view=edit_view(interaction.guild_id, interaction))
                await watch(interaction, 600)
        else:
            await interaction.response.send_message(content='You do not have permission to edit the menu.')
            
async def setup(bot):
    await bot.add_cog(menuedit(bot))