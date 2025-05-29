# 此檔案請修改 12-13 行 #

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import pytz
from datetime import datetime
import json
import traceback

json_file = "REMIND_FILE_PATH"  # Replace with the actual path to your reminders JSON file
template = "TEMPLATE_FILE_PATH"  # Replace with the actual path to your templates JSON file

def get_text(num, time, interval, channel):
    return f'編號：{num}\n時間：{format_none(time)}\n頻率：{format_none(format_interval(interval))}\n頻道：{format_none(format_channel(channel))}\n\n內容：'

def get_time_no_str():
    taiwan_tz = pytz.timezone("Asia/Taipei")
    t = datetime.now(pytz.UTC).astimezone(taiwan_tz)
    t = t.replace(tzinfo=None)
    return t

def format_none(value):
    if value is None:
        return '無'
    else:
        return value

def valid(a, minv, maxv):
    if a == '':
        return 0
    try:
        #print('is not empty') 
        a = int(a)
        if minv <= a <= maxv:
            return a
        else:
            return None
    except ValueError:
        return None 
        

def dump_json(data, num, settings):
    data[str(num)] = settings
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)
    
def format_interval(interval):
    if interval:
        days = interval['days']
        hours = interval['hours']
        minutes = interval['minutes']
        seconds = interval['seconds']
        return f'{days}天 {hours}小時 {minutes}分鐘 {seconds}秒'
    else:
        return None
    
def format_channel(channel):
    if channel:
        return f'<#{channel}>'
    else:
        return None

def check_embed(num, submit = 0):
    with open(json_file, 'r') as f:
        data = json.load(f)
    settings = data.get(str(num), None)
    
    if submit == 0:
        remind_content = discord.Embed(title=format_none(settings["title"]),
                                        description=format_none(settings["description"]),
                                        color=0xffffff)
        remind_content.set_image(url=settings["image"])
        return remind_content, settings['time'], settings['interval'], settings['channel']
    else:
        remind_content = discord.Embed(title=settings["title"],
                                        description=settings["description"],
                                        color=0xffffff)
        remind_content.set_image(url=settings["image"])
        return remind_content, settings['time'], settings['interval'], settings['channel']

def get_data():
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def delete_data(num):
    with open(json_file, 'r') as f:
        data = json.load(f)
    if str(num) in data:
        del data[str(num)]
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)


class time_modal(discord.ui.Modal, title = '輸入時間'):
    def __init__(self, settings, num, bot, edit):
        super().__init__(timeout = 600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.edit = edit
        self.time = discord.ui.TextInput(label = "使用半形 6碼 ex. 132000 (13:20:00)", placeholder = "000000", min_length = 6, max_length = 6, style=discord.TextStyle.short, default=self.settings['time'].split(' ')[1].replace(':', '') if self.settings['time'] else None)
        self.date = discord.ui.TextInput(label = "使用半形，yyyymmdd ex. 20251231", placeholder = "20251231", min_length = 8, max_length = 8, style=discord.TextStyle.short, default=self.settings['time'].split(' ')[0].replace('-', '') if self.settings['time'] else None)
        self.add_item(self.date)
        self.add_item(self.time)

    async def on_submit(self, interaction: discord.Interaction):
        self.d = self.date.value[:4] + '-' + self.date.value[4:6] + '-' + self.date.value[6:]
        self.t = self.time.value[:2] + ':' + self.time.value[2:4] + ':' + self.time.value[4:]
        t = self.d + ' ' + self.t
        # print(t)  
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = self.edit)     
        try: 
            datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            if datetime.strptime(t, "%Y-%m-%d %H:%M:%S") > get_time_no_str():
                self.settings['time'] = t 
                dump_json(get_data(), self.num, self.settings)
                remind_content, t, interval, channel = check_embed(self.num)
                content = get_text(self.num, t, interval, channel)
                await interaction.response.edit_message(content=f'## ✅已設定時間\n目前設定內容：\n{content}', embed=remind_content, view=view)
            else:
                remind_content, t, interval, channel = check_embed(self.num)
                content = get_text(self.num, t, interval, channel)
                await interaction.response.edit_message(content=f'## ❌時間已過，請重新設定未來時間\n目前設定內容：\n{content}', embed=remind_content, view=view)
        except:
            remind_content, t, interval, channel = check_embed(self.num)
            content = get_text(self.num, t, interval, channel)
            await interaction.response.send_message(content=f'## ❌時間格式錯誤，請重新輸入\n目前設定內容：\n{content}', embed=remind_content, view=view)

class interval_modal(discord.ui.Modal, title = '輸入頻率'):
    def __init__(self, settings, num, bot, edit):
        super().__init__(timeout = 600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.edit = edit
        self.days = discord.ui.TextInput(label = "天 (選填)", placeholder = "填入 1 ~ 365 的半形整數", style=discord.TextStyle.short, required=False, default=self.settings['interval']['days'] if self.settings['interval'] else None)
        self.hours = discord.ui.TextInput(label = "小時 (選填)", placeholder = "填入 1 ~ 23 的半形整數", style=discord.TextStyle.short, required=False, default=self.settings['interval']['hours'] if self.settings['interval'] else None)
        self.minutes = discord.ui.TextInput(label = "分鐘 (選填)", placeholder = "填入 1 ~ 59 的半形整數", style=discord.TextStyle.short, required=False, default=self.settings['interval']['minutes'] if self.settings['interval'] else None)
        self.seconds = discord.ui.TextInput(label = "秒 (選填)", placeholder = "填入 1 ~ 59 的半形整數", style=discord.TextStyle.short, required=False, default=self.settings['interval']['seconds'] if self.settings['interval'] else None)
        self.add_item(self.days)
        self.add_item(self.hours)
        self.add_item(self.minutes)
        self.add_item(self.seconds)
        

    async def on_submit(self, interaction: discord.Interaction):
        d = self.days.value.strip()
        h = self.hours.value.strip()
        m = self.minutes.value.strip()
        s = self.seconds.value.strip()
        d, h, m, s = valid(d, 0, 365), valid(h, 0, 23), valid(m, 0, 59), valid(s, 0, 59)

        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = self.edit)
        if d == None or h == None or m == None or s == None: 
            remind_content, t, interval, channel = check_embed(self.num)
            content = get_text(self.num, t, interval, channel)
            await interaction.response.edit_message(content=f'## ❌輸入錯誤，請重新輸入\n{content}', embed=remind_content, view=view)

        elif d == h == m == s == 0:
            remind_content, t, interval, channel = check_embed(self.num)
            content = get_text(self.num, t, interval, channel)
            await interaction.response.edit_message(content=f'## ❌輸入錯誤，若要重複提醒請至少輸入一個數字\n{content}', embed=remind_content, view=view)
            
        else:
            self.settings['interval'] = {'days': d, 'hours': h, 'minutes': m, 'seconds': s}
            #print(self.settings['interval'])
            dump_json(get_data(), self.num, self.settings)
            remind_content, t, interval, channel = check_embed(self.num)
            content = get_text(self.num, t, interval, channel)
            await interaction.response.edit_message(content=f'## ✅已設定頻率，目前設定內容：\n{content}', embed=remind_content, view=view)

class channel_select(discord.ui.ChannelSelect):
    def __init__(self, settings, num, i, bot, edit):
        super().__init__(placeholder = "請選擇", custom_id = 'channel_select', min_values=1, max_values=1, channel_types=[discord.ChannelType.text]) #, options = [])
        self.settings = settings
        self.num = num
        self.i = i
        self.bot = bot
        self.edit = edit
        # guild = self.bot.get_guild(self.settings['id'])
        # for channel in guild.text_channels:
        #     self.add_option(label = channel.name, value = channel.id)

    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.message.delete()

    async def send(self, interaction: discord.Interaction):
        self.message = await interaction.response.send_message(content="請選擇頻道", embed=None, view=channel_select_view(self.settings, self.num, interaction, self.bot))

    async def callback(self, interaction: discord.Interaction):
        self.settings['channel'] = self.values[0].id
        dump_json(get_data(), self.num, self.settings)
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = self.edit)
        await interaction.message.delete()
        await self.i.message.edit(content=f'## ✅已設定頻道，目前設定內容：\n{content}', embed=remind_content, view=view)

class channel_select_view(discord.ui.View):
    def __init__(self, settings, num, interaction, bot, edit):
        super().__init__()
        self.add_item(channel_select(settings, num, interaction, bot, edit))

class template_select(discord.ui.Select):   
    def __init__(self, settings, num, i, bot, edit):
        super().__init__(placeholder = "請選擇", custom_id = 'template_select', min_values=1, max_values=1)
        self.settings = settings
        self.num = num
        self.i = i
        self.bot = bot
        
        with open(template, 'r') as f: self.t_data = json.load(f)
        self.l = [j for j in self.t_data if self.t_data[j]['id'] == self.settings['id']]
        for i in self.l:
            self.add_option(label = self.t_data[i]['name'], value = i)

    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.message.delete()

    async def not_found(self):
        if not self.l:
            return True
        else:
            return False

    async def callback(self, interaction: discord.Interaction):
        self.t_num = int(self.values[0])
        self.t_settings = self.t_data[str(self.t_num)]
        self.settings['title'], self.settings['description'], self.settings['image'], self.settings['time'], self.settings['interval'], self.settings['channel'] = self.t_settings['title'], self.t_settings['description'], self.t_settings['image'], self.t_settings['time'], self.t_settings['interval'], self.t_settings['channel']
        dump_json(get_data(), self.num, self.settings)
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = 0)
        await interaction.message.delete()
        await self.i.message.edit(content=f'## ✅已匯入模板，目前設定內容：\n{content}', embed=remind_content, view=view)

class template_select_view(discord.ui.View):
    def __init__(self, settings, num, interaction, bot, edit):
        super().__init__()
        self.add_item(template_select(settings, num, interaction, bot, edit))

class title_modal(discord.ui.Modal, title = '輸入標題'):
    def __init__(self, settings, num, bot, edit):
        super().__init__(timeout = 600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.edit = edit
        self.title_input = discord.ui.TextInput(label = "請輸入標題", placeholder = "標題", min_length = 1, max_length = 256, style=discord.TextStyle.short)
        self.add_item(self.title_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        self.settings['title'] = self.title_input.value
        dump_json(get_data(), self.num, self.settings)
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user=interaction.user, edit = self.edit)
        await interaction.response.edit_message(content=f'## ✅已設定標題，目前設定內容：\n{content}', embed=remind_content, view=view)

class description_modal(discord.ui.Modal, title = '輸入內容'):
    def __init__(self, settings, num, bot, edit):
        super().__init__(timeout = 600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.edit = edit
        self.description = discord.ui.TextInput(label = "請輸入內容", placeholder = "內容", min_length = 1, max_length = 2048, style=discord.TextStyle.long)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        self.settings['description'] = self.description.value
        dump_json(get_data(), self.num, self.settings)
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = self.edit)
        await interaction.response.edit_message(content=f'## ✅已設定內容，目前設定內容：\n{content}', embed=remind_content, view=view)

class image_modal(discord.ui.Modal, title = '輸入影像連結'):
    def __init__(self, settings, num, bot, edit):
        super().__init__(timeout = 600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.edit = edit
        self.image = discord.ui.TextInput(label = "請輸入影像連結 (輸入 'cancel' 刪除圖片)", placeholder = "連結", min_length = 1, max_length = 2048, style=discord.TextStyle.short)
        self.add_item(self.image)

    async def on_submit(self, interaction: discord.Interaction):
        self.settings['image'] = self.image.value
        if self.settings['image'].strip().lower() == 'cancel': self.settings['image'] = None
        dump_json(get_data(), self.num, self.settings)
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = self.edit)
        await interaction.response.edit_message(content=f'## ✅已設定影像連結，目前設定內容：\n{content}', embed=remind_content, view=view)

class name_template_modal(discord.ui.Modal, title = '為模板取個名字吧'):
    def __init__(self, settings, num, bot):
        super().__init__(timeout = 600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.name = discord.ui.TextInput(label = "請輸入名字", placeholder = "名字", min_length = 1, max_length = 256, style=discord.TextStyle.short)
        self.add_item(self.name)
        
    async def on_submit(self, interaction: discord.Interaction):
        self.settings['name'] = self.name.value
        with open(template, 'r') as f: self.t_data = json.load(f)
        if self.t_data:
            self.t_num = max(map(int, self.t_data.keys())) + 1
        else:
            self.t_num = 1
        self.t_data[self.t_num] = self.settings
        with open(template, 'w') as f:
            json.dump(self.t_data, f, indent=4)
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit = 0)
        await interaction.response.edit_message(content=f'## ✅已儲存模板，目前設定內容：\n{content}', embed=remind_content, view=view)

class disabled_remind_buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="取消編輯", style=discord.ButtonStyle.danger, emoji="❌", disabled=True)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        return
    
    @discord.ui.button(label="完成", style=discord.ButtonStyle.success, emoji="✅", disabled=True)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        return      
    
    @discord.ui.button(label="提醒時間", style=discord.ButtonStyle.primary, emoji="⏰", disabled=True)
    async def time(self, interaction: discord.Interaction, button: discord.ui.Button):
        return
    
    @discord.ui.button(label="提醒頻率", style=discord.ButtonStyle.primary, emoji="🔁", disabled=True)
    async def interval(self, interaction: discord.Interaction, button: discord.ui.Button):
        return
    
    @discord.ui.button(label="提醒頻道", style=discord.ButtonStyle.primary, emoji="📢", disabled=True)
    async def channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        return
    
    @discord.ui.button(label="訊息標題", style=discord.ButtonStyle.primary, emoji="📝", disabled=True)
    async def title(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label="訊息內容", style=discord.ButtonStyle.primary, emoji="📄", disabled=True)
    async def description(self, interaction: discord.Interaction, button: discord.ui.Button):
        return
    
    @discord.ui.button(label="插入圖片", style=discord.ButtonStyle.primary, emoji="🖼️", disabled=True)
    async def image(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label="儲存模板", style=discord.ButtonStyle.primary, emoji="💾", disabled=True)
    async def save_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label="匯入模板", style=discord.ButtonStyle.primary, emoji="📥", disabled=True)
    async def import_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

class disabled_examine_reminder_buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label = "", style = discord.ButtonStyle.gray, emoji="⬅️", disabled=True)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label = "刪除", style = discord.ButtonStyle.danger, emoji="❌", disabled=True)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label = "編輯", style = discord.ButtonStyle.blurple, emoji="📝", disabled=True)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label = "", style = discord.ButtonStyle.gray, emoji="➡️", disabled=True)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

class create_remind_buttons(discord.ui.View):
    def __init__(self, settings, num, bot, i_user = None, i: discord.Interaction = None, edit = 0):
        super().__init__(timeout=600)
        self.settings = settings
        self.num = num
        self.bot = bot
        self.i_user = i_user 
        self.i = i
        # print(type(self.i))
        self.edit = edit

        if self.edit: 
            self.remove_item(self.cancel)
            self.remove_item(self.save_template)
            self.remove_item(self.import_template)

    async def select_callback(self, interaction: discord.Interaction):
        self.num = int(interaction.data['values'][0])
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        self.left.disabled = (self.num == int(self.l[0]))
        self.right.disabled = (self.num == int(self.l[-1]))
        await interaction.response.edit_message(content=content, embed=remind_content, view=self)

    async def on_timeout(self):
        print('timeout')
        try:
            self.done = get_data()[str(self.num)]['done']
            if not self.done:
                delete_data(self.num)
                try:
                    await self.i.edit_original_response(content="## 訊息已逾時\n", view=disabled_remind_buttons())
                    return
                except Exception as e:
                    print(traceback.format_exc())
                    return
            else:
                return
        except Exception as e:
            print(e)
            return
            

    @discord.ui.button(label="取消編輯", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            delete_data(self.num) #, edit=self.edit)
            await interaction.response.edit_message(content="已取消編輯😒", embed=None, view=None)
    
    @discord.ui.button(label="完成", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            #print(self.i_user, interaction.user)
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:

                remind_content, t, interval, channel = check_embed(self.num)
                if self.settings['time'] and self.settings['title'] and self.settings['description'] and self.settings['channel']:

                    if datetime.strptime(t, "%Y-%m-%d %H:%M:%S") <= get_time_no_str(): 
                        content = get_text(self.num, t, interval, channel)
                        view = self
                        await interaction.response.edit_message(content=f"## ❌時間已過，請重新設定未來時間\n{content}", embed=remind_content, view=view) 
                    else:
                        remind_content, t, interval, channel = check_embed(self.num, submit = 1) #, edit = self.edit)
                        view = self
                        content = get_text(self.num, t, interval, channel)
                        self.settings['done'] = True
                        dump_json(get_data(), self.num, self.settings)
                        # if self.edit == 1: delete_data(self.num, edit = 1)
                        await interaction.response.edit_message(content=f'已設定完成以下內容：\n{content}', embed=remind_content, view=None) 

                else: 
                    view = self
                    content = get_text(self.num, t, interval, channel)
                    await interaction.response.edit_message(content=f"## ❌時間、頻道、標題與內容為必填項目\n{content}", embed=remind_content, view=view)                


    @discord.ui.button(label="提醒時間", style=discord.ButtonStyle.primary, emoji="⏰")
    async def time(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            await interaction.response.send_modal(time_modal(self.settings, self.num, self.bot, self.edit))

    @discord.ui.button(label="提醒頻率", style=discord.ButtonStyle.primary, emoji="🔁")
    async def interval(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            await interaction.response.send_modal(interval_modal(self.settings, self.num, self.bot, self.edit))

    @discord.ui.button(label="取消頻率", style=discord.ButtonStyle.primary, emoji="❌")
    async def cancel_interval(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            self.settings['interval'] = None
            dump_json(get_data(), self.num, self.settings)
            remind_content, t, interval, channel = check_embed(self.num)
            content = get_text(self.num, t, interval, channel)
            view = create_remind_buttons(self.settings, self.num, self.bot, i_user = interaction.user, edit=self.edit)
            await interaction.response.edit_message(content=f'## ✅已取消頻率，目前設定內容：\n{content}', embed=remind_content, view=view)

    @discord.ui.button(label="提醒頻道", style=discord.ButtonStyle.primary, emoji="📢")
    async def channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            try:
                await interaction.response.send_message(content="請選擇頻道", embed=None, view=channel_select_view(self.settings, self.num, interaction, self.bot, self.edit))
            except Exception as e:
                print(e)

    @discord.ui.button(label="訊息標題", style=discord.ButtonStyle.primary, emoji="📝")
    async def title(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            await interaction.response.send_modal(title_modal(self.settings, self.num, self.bot, self.edit))

    @discord.ui.button(label="訊息內容", style=discord.ButtonStyle.primary, emoji="📄")
    async def description(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            await interaction.response.send_modal(description_modal(self.settings, self.num, self.bot, self.edit))

    @discord.ui.button(label="插入圖片", style=discord.ButtonStyle.primary, emoji="🖼️")
    async def image(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            await interaction.response.send_modal(image_modal(self.settings, self.num, self.bot, self.edit))

    @discord.ui.button(label="儲存模板", style=discord.ButtonStyle.primary, emoji="💾")
    async def save_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            await interaction.response.send_modal(name_template_modal(self.settings, self.num, self.bot))

    @discord.ui.button(label="匯入模板", style=discord.ButtonStyle.primary, emoji="📥")
    async def import_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            # print(template_select.not_found())
            # if await template_select.not_found():
            #     await interaction.response.send_message(content="沒有可匯入的模板", embed=None, view=None)
            # else:
            await interaction.response.send_message(content="請選擇模板", embed=None, view=template_select_view(self.settings, self.num, interaction, self.bot, self.edit))

                    

class examine_reminder_buttons(discord.ui.View):
    def __init__(self, bot, i_user = None, i = None):
        super().__init__(timeout=600)
        
        self.data = get_data()
        self.bot = bot
        self.i_user = i_user
        self.i = i
        self.id = i.guild_id
        self.l = [j for j in self.data if self.data[j]['id'] == self.id and self.data[j]['done']]
        
        if self.l:
            # sort with time order
            self.l = sorted(self.l, key=lambda x: datetime.strptime(self.data[x]['time'], "%Y-%m-%d %H:%M:%S"))
            self.num = int(self.l[0])    
            ind = 0
            for i in range(len(self.l) // 25 + 1):
                options = []
                for j in range(25):
                    if ind < len(self.l):
                        #print(self.l[ind])
                        options.append(discord.SelectOption(label = self.l[ind] + ' - ' + self.data[self.l[ind]]['title'], value = self.l[ind]))
                        ind += 1
                
                select = discord.ui.Select(placeholder = "請選擇", custom_id = f'examine_select{i+1}', options = options)
                
                select.callback = self.select_callback
                self.add_item(select)       
        
    async def select_callback(self, interaction: discord.Interaction):
        
        self.num = int(interaction.data['values'][0])
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        self.left.disabled = (self.num == int(self.l[0]))
        self.right.disabled = (self.num == int(self.l[-1]))
        await interaction.response.edit_message(content=content, embed=remind_content, view=self)
        
    async def on_timeout(self):
        print('timeout')
        # for child in self.children:
        #     child.disabled = True
        try:
            # print(self.i.content) # discord.interactions.Interaction.message.content
            await self.i.edit_original_response(content="## 訊息已逾時\n", view=disabled_examine_reminder_buttons()) # + self.i.message.content) #)
        except Exception as e:
            # pass
            print(e)
    
    @discord.ui.button(label = "", style = discord.ButtonStyle.gray, emoji="⬅️", disabled=True)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        ind = self.l.index(str(self.num)) - 1
        self.num = int(self.l[ind])
        button.disabled = False
        self.right.disabled = False
        if ind == 0: button.disabled = True
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        await interaction.response.edit_message(content=content, embed=remind_content, view=self)

    @discord.ui.button(label = "刪除", style = discord.ButtonStyle.danger, emoji="❌")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            delete_data(self.num)
            await interaction.response.edit_message(content="已刪除", embed=None, view=None)

    # @discord.ui.button(label = "", style = discord.ButtonStyle.blurple, emoji="🔃")
    # async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     self.clear_items()
    #     if self.l:
    #         self.num = int(self.l[0])    
    #         ind = 0
    #         for i in range(len(self.l) // 25 + 1):
    #             options = []
    #             for j in range(25):
    #                 if ind < len(self.l):
    #                     #print(self.l[ind])
    #                     options.append(discord.SelectOption(label = self.l[ind] + ' - ' + self.data[self.l[ind]]['title'], value = self.l[ind]))
    #                     ind += 1
                
    #             select = discord.ui.Select(placeholder = "請選擇", custom_id = f'examine_select{i+1}', options = options)
                
    #             select.callback = self.select_callback
    #             self.add_item(select)

    @discord.ui.button(label = "編輯", style = discord.ButtonStyle.blurple, emoji="📝")
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i_user != interaction.user: 
            await interaction.response.send_message(content="沒事不要亂按87", embed=None, view=None, ephemeral=True)
        else:
            settings = get_data()[str(self.num)]
            view = create_remind_buttons(settings, self.num, self.bot, i_user = interaction.user, i = interaction, edit = 1)
            remind_content, t, interval, channel = check_embed(self.num)
            content = get_text(self.num, t, interval, channel)
            await interaction.response.edit_message(content=f'目前設定內容：\n{content}', embed=remind_content, view=view)

    @discord.ui.button(label = "", style = discord.ButtonStyle.gray, emoji="➡️")
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        ind = self.l.index(str(self.num)) + 1
        self.num = int(self.l[ind])
        button.disabled = False
        self.left.disabled = False
        if ind == len(self.l)-1: button.disabled = True
        remind_content, t, interval, channel = check_embed(self.num)
        content = get_text(self.num, t, interval, channel)
        await interaction.response.edit_message(content=content, embed=remind_content, view=self)    

class remind(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create_reminder", description="新增提醒")
    async def create_reminder(self, interaction: discord.Interaction):
        interaction.response.defer(thinking=True)
        guild_id = interaction.guild.id
        settings = {'id': guild_id, 'title': None, 'description': None, 'time': None, 'channel': None, 'interval': None, 'image': None, 'done': False}
        with open(json_file, 'r') as f: data = json.load(f)
        if data:
            num = max(map(int, data.keys())) + 1
        else:
            num = 1
        dump_json(data, num, settings)
        try:
            remind_content, t, interval, channel = check_embed(num)
        except Exception as e:
            print(e)
        content = get_text(num, t, interval, channel)
        await interaction.response.send_message(content=f'目前設定內容：\n{content}' , embed=remind_content) #, view=None)
        m = await interaction.original_response()
        view = create_remind_buttons(settings, num, self.bot, i_user = interaction.user, i = interaction)
        await m.edit(view=view)

    @app_commands.command(name="examine_reminder", description="查看提醒")
    async def examine_reminder(self, interaction: discord.Interaction):
        data = get_data()
        try:
            
            l = [j for j in data if data[j]['id'] == interaction.guild_id and data[j]['done']]
            
            num = l[0] 
            
            remind_content, t, interval, channel = check_embed(num)
            content = get_text(num, t, interval, channel)
            # 
            view = examine_reminder_buttons(self.bot, i_user = interaction.user, i = interaction)
            if len(l) == 1: view.right.disabled = True
            
            await interaction.response.send_message(content=content, embed=remind_content, view=view)
            # print(interaction.message)
        except Exception as e:
            print(e)
            await interaction.response.send_message(content="無提醒")

async def setup(bot: commands.Bot):
    await bot.add_cog(remind(bot))

        