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
cart = "CART_FILE_PATH"  # Replace with the actual path to your cart file
cogs_folder_path = "COGS_FOLDER_PATH"  # Replace with the actual path to your cogs folder

def del_cart(guild_id, table_num):
    cart_data = json.load(open(cart, 'r'))
    if table_num in cart_data[str(guild_id)]:
        del cart_data[str(guild_id)][table_num]
        json.dump(cart_data, open(cart, 'w'), indent=4)

def make_menu(menu, guild_name):
    embed = discord.Embed(title=f"{guild_name}'s Menu", description=menu['description'], color=discord.Colour.from_rgb(111, 162, 242))
    items, prices = [], []
    for item in menu['items']:
        items.append(item)
        prices.append('$ ' + str(menu['items'][item]))
    embed.add_field(name='item', value='\n'.join(items), inline=True)
    embed.add_field(name='price', value='\n'.join(prices), inline=True)
    return embed

def make_cart(menu, cart, table_num):
    embed = discord.Embed(title=f"🛒 Shopping Cart", 
                          color=discord.Colour.from_rgb(111, 162, 242))
    if not cart[str(table_num)]['items']:
        embed.add_field(name='item', value='None', inline=True)
        embed.add_field(name='price', value='None', inline=True)
        embed.add_field(name='quantity', value='None', inline=True)
    else:
        items, prices, quantities = [], [], []
        for item in cart[str(table_num)]['items']:
            items.append(item)
            prices.append('$ ' + str(menu['items'][item]))
            quantities.append(str(cart[str(table_num)]['items'][item]))
        embed.add_field(name='item', value='\n'.join(items), inline=True)
        embed.add_field(name='price', value='\n'.join(prices), inline=True)
        embed.add_field(name='quantity', value='\n'.join(quantities), inline=True)

    embed.description = f'''
                        Table Number {table_num}\n
                        Notes: {cart[str(table_num)]['notes'] if cart[str(table_num)]['notes'] else 'None'}\n
                        Total: $ {sum([menu['items'][item] * cart[str(table_num)]['items'][item] for item in cart[str(table_num)]['items']])}
                        '''
    return embed

        
async def watch(interaction: discord.Interaction, seconds=180, embeds=False, table_num=0):  
    event_handler = filechange_handler(
                    interaction,
                    interaction.guild_id,
                    embeds=embeds,
                    table_num=table_num,
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

# Custom event handler that gets a reference to the interaction
class filechange_handler(PatternMatchingEventHandler):
    def __init__(self, interaction: discord.Interaction, guild_id, embeds = False, table_num = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.guild_id = guild_id
        self.embeds = embeds
        self.table_num = table_num

    def on_modified(self, event):
        asyncio.run_coroutine_threadsafe(self.update_interaction(), self.interaction.client.loop)

    async def update_interaction(self):
        updated_content = "The file has been updated!"
        try:
            data = json.load(open(menu_file, 'r'))
            embed = make_menu(data[str(self.guild_id)], self.interaction.guild.name)
            if not self.embeds:
                await self.interaction.edit_original_response(embed=embed)
            else:
                cart_data = json.load(open(cart, 'r'))
                cart_embed = make_cart(data[str(self.guild_id)], cart_data[str(self.guild_id)], self.table_num)
                await self.interaction.edit_original_response(embeds=[embed, cart_embed])
        except Exception as e:
            print(traceback.format_exc())

class order_buttons(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, table_num):
        self.table_num = table_num
        super().__init__(timeout=600)
        self.interaction = interaction
        self.selected_item = None
        self.selected_quantity = None

        with open(menu_file, 'r') as f:
            self.menu = json.load(f)[str(interaction.guild_id)]['items']

        item_select = discord.ui.Select(
            placeholder='Select an item',
            options=[discord.SelectOption(label=item, value=item) for item in self.menu.keys()],
            min_values=1,
            max_values=1
        )
        

        quantity_select = discord.ui.Select(
            placeholder='Select a quantity',
            options=[discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 11)],
            min_values=1,
            max_values=1
        )

        item_select.callback = self.item_select_callback
        quantity_select.callback = self.quantity_select_callback
        self.add_item(item_select)
        self.add_item(quantity_select)

    async def item_select_callback(self, interaction: discord.Interaction):
        # print('hello')
        try:
            
            await interaction.response.defer()
            self.selected_item = interaction.data['values'][0]
            # print(self.selected_item)
        except:
            print(traceback.format_exc())

    async def quantity_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_quantity = int(interaction.data['values'][0])

        
    async def on_timeout(self):
        await self.interaction.edit_original_response(content='Expired', embeds=[], view=None)

    @discord.ui.button(label="Order", style=discord.ButtonStyle.success, emoji=discord.PartialEmoji.from_str('<:chiumiddle:1339509570619576372>'))
    async def order(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            menu_data = json.load(open(menu_file, 'r'))
            cart_data = json.load(open(cart, 'r'))
            cart_data[str(self.interaction.guild_id)][self.table_num]['done'] = True
            json.dump(cart_data, open(cart, 'w'), indent=4)
            cart_embed = make_cart(menu_data[str(self.interaction.guild_id)], cart_data[str(self.interaction.guild_id)], self.table_num)
            await self.interaction.edit_original_response(content='Order placed!', embeds=[cart_embed], view=None)
        except:
            print(traceback.format_exc())

    @discord.ui.button(label="Edit Notes", style=discord.ButtonStyle.primary)
    async def edit_notes(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(notes_modal(interaction.guild_id, self.table_num))
        except:
            print(traceback.format_exc())

    @discord.ui.button(label="Add to Cart", style=discord.ButtonStyle.primary)
    async def add_to_cart(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.selected_item is None or self.selected_quantity is None:
                await self.interaction.followup.send('Please select an item and quantity.', ephemeral=True)
                return

            cart_data = json.load(open(cart, 'r'))
            if self.selected_item not in cart_data[str(self.interaction.guild_id)][self.table_num]['items']:
                cart_data[str(self.interaction.guild_id)][self.table_num]['items'][self.selected_item] = self.selected_quantity
            else:
                cart_data[str(self.interaction.guild_id)][self.table_num]['items'][self.selected_item] += self.selected_quantity    
            json.dump(cart_data, open(cart, 'w'), indent=4)
            menu = json.load(open(menu_file, 'r'))
            menu_embed = make_menu(menu[str(self.interaction.guild_id)], self.interaction.guild.name)
            cart_embed = make_cart(menu[str(self.interaction.guild_id)], cart_data[str(self.interaction.guild_id)], self.table_num)
            await self.interaction.edit_original_response(embeds=[menu_embed, cart_embed])
        except:
            print(traceback.format_exc())
        
    @discord.ui.button(label="Remove from Cart", style=discord.ButtonStyle.primary)
    async def remove_from_cart(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if self.selected_item is None or self.selected_quantity is None:
                await self.interaction.followup.send('Please select an item and quantity.', ephemeral=True)
                return
            cart_data = json.load(open(cart, 'r'))
            if self.selected_item in cart_data[str(self.interaction.guild_id)][self.table_num]['items']:
                if cart_data[str(self.interaction.guild_id)][self.table_num]['items'][self.selected_item] <= self.selected_quantity:
                    del cart_data[str(self.interaction.guild_id)][self.table_num]['items'][self.selected_item]
                else:
                    cart_data[str(self.interaction.guild_id)][self.table_num]['items'][self.selected_item] -= self.selected_quantity
            else:
                await self.interaction.followup.send('Item not in cart.', ephemeral=True)
            json.dump(cart_data, open(cart, 'w'), indent=4)
            menu = json.load(open(menu_file, 'r'))
            menu_embed = make_menu(menu[str(self.interaction.guild_id)], self.interaction.guild.name)
            cart_embed = make_cart(menu[str(self.interaction.guild_id)], cart_data[str(self.interaction.guild_id)], self.table_num)
            await self.interaction.edit_original_response(embeds=[menu_embed, cart_embed])
        except:
            print(traceback.format_exc())

class table_num_modal(discord.ui.Modal, title='Table Number'):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.table_num_input = discord.ui.TextInput(label='table num:', placeholder='Enter table number', min_length=1, max_length=3, required=True)
        self.add_item(self.table_num_input)

    async def on_submit(self, interaction: discord.Interaction):
        table_num = self.table_num_input.value.strip()
        cart_data = json.load(open(cart, 'r'))
        if str(interaction.guild_id) not in cart_data:
            cart_data[str(interaction.guild_id)] = {}
        try: 
            if table_num in cart_data[str(interaction.guild_id)]:
                await interaction.response.send_message('Table number already in use.', ephemeral=True)
                return
            else:
                int(table_num)
                cart_data[str(interaction.guild_id)][table_num] = {'notes': '', 'items': {}, 'done': False}
                json.dump(cart_data, open(cart, 'w'), indent=4)
                menu = json.load(open(menu_file, 'r'))
                menu_embed = make_menu(menu[str(self.guild_id)], interaction.guild.name)
                cart_embed = make_cart(menu[str(self.guild_id)], cart_data[str(self.guild_id)], table_num)
                await interaction.response.send_message(embeds=[menu_embed, cart_embed], view=order_buttons(interaction, table_num))
                await watch(interaction, 600, embeds=True, table_num=table_num)

        except ValueError:
            await interaction.response.send_message('Please enter a valid number.', ephemeral=True)
        except:
            print(traceback.format_exc())

class notes_modal(discord.ui.Modal, title='Notes'):
    def __init__(self, guild_id, table_num):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.notes = json.load(open(cart, 'r'))[str(self.guild_id)][table_num]['notes']
        self.table_num = table_num
        self.notes_input = discord.ui.TextInput(label='Notes:', placeholder='Enter notes', min_length=1, max_length=1000, required=True, default=self.notes, style=discord.TextStyle.long)
        self.add_item(self.notes_input)

    async def on_submit(self, interaction: discord.Interaction):
        cart_data = json.load(open(cart, 'r'))
        cart_data[str(self.guild_id)][self.table_num]['notes'] = self.notes_input.value
        json.dump(cart_data, open(cart, 'w'), indent=4)
        menu = json.load(open(menu_file, 'r'))
        menu_embed = make_menu(menu[str(self.guild_id)], interaction.guild.name)
        cart_embed = make_cart(menu[str(self.guild_id)], cart_data[str(self.guild_id)], self.table_num)
        await interaction.response.edit_message(embeds=[menu_embed, cart_embed])

class order(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="customer_order", description="Order from the menu")
    async def customer_order(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_modal(table_num_modal(interaction.guild_id))
        except:
            print(traceback.format_exc())
            await interaction.response.send_message('Error', ephemeral=True)

async def setup(bot):
    await bot.add_cog(order(bot))
        