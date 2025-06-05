import discord, asyncio, requests, random, json, validators
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from discord import app_commands, SelectOption
from typing import List
from discord.ui import TextInput
channelId = 1341296535098626078
menu_path = '/home/jeanthegod/chiubot/testing_cog/usefulma/carrot.json'

def get_timestamp():
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f'[{timestamp_str}]'+' - {} - {}'    

# 更新菜單檔案
def renew_menu(page: str, title: str | None = '', description: str | None = '', pic:str | None = ''):
    with open(menu_path, 'r') as file:
            data = json.load(file)
    if title: data['menu'][page]['title'] = title        
    if description: data['menu'][page]['description'] = description
    if pic: data['menu'][page]['pic'] = pic
    
    if title.lower() == "none": data['menu'][page]['title'] = None       
    if description.lower() == "none": data['menu'][page]['description'] = None 
    if pic.lower() == "none": data['menu'][page]['pic'] = None 
    
    
    with open(menu_path, 'w') as file:
            json.dump(data, file, indent=4)

# 更新菜單Embed
def embed_menu(page: str):
    with open(menu_path, 'r') as file:
            data = json.load(file)

    title = data['menu'][page]['title']       
    description = data['menu'][page]['description']
    pic = data['menu'][page]['pic']
    
    embed = discord.Embed(
        title=title if title else '---',
        description= description if description else '---',
        color=discord.Color.from_rgb(110, 78, 190)
    )
    
    try: 
        if pic and validators.url(pic) or pic.startswith('https://cdn.discordapp.com/'): embed.set_image(url=pic)
    except: pass
    
    embed.add_field(name='\u200b', value=f'第{page}頁')
    
    return embed    


# 改標題 MODAL
class menuTitleModal(discord.ui.Modal, title='MENU 標題'):
    def __init__(self, page: str):
        super().__init__(timeout = 180)
        self.page = page
        self.title_ = TextInput(label=f'第{page}頁 標題 (None to remove)', placeholder='Mia is poo', max_length=256, min_length=1)
        self.add_item(self.title_)
    
    async def on_submit(self, ctx: discord.Interaction):
        title_ = self.title_.value
        print('title:   ', title_)
        renew_menu(page=self.page, title=title_)
        await ctx.response.edit_message(embed=embed_menu(page=self.page))

# 改描述 MODAL
class menuDescriptionModal(discord.ui.Modal, title='MENU 描述'):
    def __init__(self, page: str):
        super().__init__(timeout = 180)
        self.page = page
        self.description = TextInput(label=f'第{page}頁 描述 (None to remove)', placeholder='AB is GAY', max_length=4000, min_length=1, style=discord.TextStyle.long)
        self.add_item(self.description)
    
    async def on_submit(self, ctx: discord.Interaction):
        description = self.description.value
        renew_menu(page=self.page, description=description)
        await ctx.response.edit_message(embed=embed_menu(page=self.page))

# 改圖片online MODAL
class menuPicModal(discord.ui.Modal, title='MENU 圖片'):
    def __init__(self, page: str):
        super().__init__(timeout = 180)
        self.page = page
        self.pic = TextInput(label=f'第{page}頁 圖片 (None to remove)', placeholder='Fish is 卒', max_length=1000, min_length=1)
        self.add_item(self.pic)
    
    async def on_submit(self, ctx: discord.Interaction):
        try: 
            pic = self.pic.value
            print(pic)
            renew_menu(page=self.page, pic=pic)
            await ctx.response.edit_message(embed=embed_menu(page=self.page))
        except Exception as e:
            print(e)

# 改圖片local FUNC
async def menuPicLocal(ctx: discord.Interaction, page: str):
    try: 
        await ctx.response.send_message(content=f'please send the photo u want to add to page {page} in 60 sec')
        def check(msg: discord.Message):
            return msg.author == ctx.user and msg.attachments
        
        msg = await ctx.client.wait_for("message", timeout=60, check=check)
        attachment = msg.attachments[0]
        print('ohlala')
        if not attachment.content_type.startswith("image/"): pass
        else: 
            renew_menu(page = page, pic = attachment.url)
            print('get ur pic cha')
        await ctx.delete_original_response()
        #await ctx.response.edit_message(embed=embed_menu(page = str(self.page + 1)))
            
            
    except Exception as e: print(e)
    



class weatherView(discord.ui.View):
    
    def __init__(self, date):
        super().__init__(timeout=86400)
        self.weather = self.bugWeather()  # 呼叫 bugWeather 函數並獲得資料
        self.date = date
        
    def bugWeather(self):
        api = 'CWA-129B2CAC-422F-4A14-92F8-556457328D75'
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        params = {
            "Authorization": api,
            "format": "JSON"
        }

        response = requests.get(url, params=params)
        data = response.json()['records']['location']
        weather_report = {}
        for i in data:
            city = i['locationName']    # 縣市名稱
            wx = i['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
            maxt = i['weatherElement'][4]['time'][0]['parameter']['parameterName']  # 最高溫
            mint = i['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最低溫
            ci = i['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
            pop = i['weatherElement'][1]['time'][0]['parameter']['parameterName']   # 降雨機率
            
            weather_report[city] = {
                '天氣現象': wx,
                '最高溫度': maxt,
                '最低溫度': mint,
                '舒適度': ci,
                '降雨機率': pop
            }
            
        return weather_report

    @discord.ui.select(
        placeholder='which city', 
        max_values=1,
        min_values=1,
        options=[
            SelectOption(label=city, value=city) for city in [
                "嘉義縣", "新北市", "嘉義市", "新竹縣", "新竹市", "臺北市", "臺南市",
                "宜蘭縣", "苗栗縣", "雲林縣", "花蓮縣", "臺中市", "臺東縣", "桃園市",
                "南投縣", "高雄市", "金門縣", "屏東縣", "基隆市", "澎湖縣", "彰化縣", "連江縣"
            ]
        ]
    )
    async def select_city(self, ctx: discord.Interaction, select: discord.ui.Select):
        city = select.values[0]
        
        embed = discord.Embed(
            title='天氣預報 ' + self.date, 
            description=city,
            color=0x1b49de  
        )
        embed.add_field(name='\u200b', value='', inline=False)
        a, b = '', ''
        for key, val in self.weather[city].items():
            a += key + '\n\n'
            b += val + '\n\n'
            
        embed.add_field(name=a, value='')
        embed.add_field(name=b, value='')
        
        await ctx.response.edit_message(embed=embed)

    async def on_timeout(self):
        print(get_timestamp().format('weather selection timeout', None))

class airqualityView(discord.ui.View):
    
    def __init__(self, date):
        super().__init__(timeout=86400)
        self.airquality = self.bugAirQuality()
        self.date = date
    def bugAirQuality(self):
        url = 'https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=9e565f9a-84dd-4e79-9097-d403cae1ea75&limit=1000&sort=ImportDate%20desc&format=JSON'
        data = requests.get(url)             # 使用 get 方法透過空氣品質指標 API 取得內容
        data_json = data.json()              # 將取得的檔案轉換為 JSON 格式
        air_quality = {}
        for i in data_json['records']: 
            information = {
                'sitename' : i['sitename'],
                'aqi' : i['aqi'],
                'status' : i['status']
            }
            
            if i['county'] in air_quality: 
                air_quality[i['county']].append(information)
            else:
                air_quality[i['county']] = []
                air_quality[i['county']].append(information)
        return air_quality

    @discord.ui.select(
        placeholder='which city', 
        max_values=1,
        min_values=1,
        options=[
            SelectOption(label=city, value=city) for city in [
                "嘉義縣", "新北市", "嘉義市", "新竹縣", "新竹市", "臺北市", "臺南市",
                "宜蘭縣", "苗栗縣", "雲林縣", "花蓮縣", "臺中市", "臺東縣", "桃園市",
                "南投縣", "高雄市", "金門縣", "屏東縣", "基隆市", "澎湖縣", "彰化縣", "連江縣"
            ]
        ]
    )
    async def select_city(self, ctx: discord.Interaction, select: discord.ui.Select):
        city = select.values[0]
        
        embed = discord.Embed(
            title='空氣品質 ' + self.date,
            description=city,
            color=0x1bde83  
        )
        embed.add_field(name='\u200b', value='', inline=False)
        sitename, aqi, status = '', '', ''
        for i in self.airquality[city]:
            sitename += i['sitename'] + '\n'
            aqi += i['aqi'] + '\n'
            status += i['status'] + '\n'
            
        embed.add_field(name='地區', value=sitename, inline=True)
        embed.add_field(name='AQI', value=aqi, inline=True)
        embed.add_field(name='空氣品質', value=status, inline=True)
        
        await ctx.response.edit_message(embed=embed)

    async def on_timeout(self):
        print(get_timestamp().format('air quality selection timeout', None))

class newsView(discord.ui.View):
    
    def __init__(self, date):
        super().__init__(timeout=86400)
        self.news = self.bug_etoday()
        self.date = date
        self.select_news_item = discord.ui.Select(
            placeholder='which news', 
            max_values=1,
            min_values=1,
            options=[
                SelectOption(label=new['title'] if len(new['title']) < 50 else new['title'][:50], value=str(i)) for i, new in enumerate(self.news)
            ]
        )
        self.select_news_item.callback = self.select_news  # 綁定回調函數
        self.add_item(self.select_news_item)
        
    def bug_etoday(self):
        url = 'https://www.ettoday.net/news/focus/%E9%A6%96%E9%A0%81/%E5%A8%9B%E6%A8%82%E5%85%AB%E5%8D%A6%E9%80%9A/'
        headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'}
        
        def bug_news(url):
            data = requests.get(url, headers=headers)  
            data = BeautifulSoup(data.text, 'lxml')
            images = ['https:'+ i.get('src') for i in data.find_all('img') if '▲' in str(i)]
            data = {
                'title' : data.find('h1', class_='title').text,
                'url' : url,
                'story' : '\n\n'.join([i.replace('\n', '').replace('\xa0', '') for i in data.find('div', class_='story').text.split('\n') if '▲' not in i and '[廣告]' not in i and i and '►' not in i]),
                'image' : random.choice(images) if images else None,
                'time' : data.find('time').get('datetime').split('T')[0]
            }
            return data
        
        date = requests.get(url, headers=headers)
        data = BeautifulSoup(date.text, 'lxml')
        data = [i.find('a').get('href') for i in data.find_all('h3') if 'title' in str(i) and i.find('a')][:10]
        data = [bug_news(i) for i in data]
        return data


    async def select_news(self, ctx: discord.Interaction):
        selected_index = int(self.select_news_item.values[0])
        news = self.news[selected_index]
        print('success')
        embed = discord.Embed(
            title=news['title'],
            description=news['story'],
            url=news['url'],
            color=0xebbf68  
        )
        if news['image']:  # 确保图片不为空
            embed.set_image(url=news['image'])
        
        
        await ctx.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        print(get_timestamp().format('bagua selection timeout', None))

class menuEditView(discord.ui.View):        
    
    def __init__(self, ctx: discord.Interaction, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.page = 0
        self.ctx = ctx
        self.crt_msg = None
        self.select_menu = discord.ui.Select(
            placeholder='choose pages', 
            max_values=1,
            min_values=1,
            options=[
                SelectOption(label=f'第{i + 1}頁' , value=str(i)) for i in range(25)
            ]
        )
        self.select_menu.callback = self.select_pages  # 綁定回調函數
        self.add_item(self.select_menu)
        
       
    # 下拉式選單    
    async def select_pages(self, interaction: discord.Interaction):
        self.page = int(self.select_menu.values[0])
        embed = embed_menu(page=str(self.page + 1))
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    # 上一頁
    @discord.ui.button(
        label = "", 
        style = discord.ButtonStyle.gray, 
        emoji="⬅️"
    )
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % 25
        embed = embed_menu(page=str(self.page + 1))
        await interaction.response.edit_message(content=None, embed=embed, view=self)
    
    # 下一頁
    @discord.ui.button(
        label = "", 
        style = discord.ButtonStyle.gray, 
        emoji="➡️"
    )
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % 25
        embed = embed_menu(page=str(self.page + 1))
        await interaction.response.edit_message(content=None, embed=embed, view=self)
        
    # 改標題
    @discord.ui.button(
        label='改變標題',
        style = discord.ButtonStyle.primary,
        emoji="🌚"
    )
    async def change_title(self, ctx: discord.Interaction, button: discord.ui.Button):
        try: await ctx.response.send_modal(menuTitleModal(page=str(self.page + 1)))
        except Exception as e: print(e)
        
    # 改內容   
    @discord.ui.button(
        label='改變描述',
        style = discord.ButtonStyle.green,
        emoji="💩"
    )
    async def change_description(self, ctx: discord.Interaction, button: discord.ui.Button):
        try:await ctx.response.send_modal(menuDescriptionModal(page=str(self.page + 1)))
        except Exception as e: print(e)
    
    # 改圖片(網址)
    @discord.ui.button(
        label='改變圖片(online pic)',
        style = discord.ButtonStyle.gray,
        emoji="❤️‍🔥"
    )
    async def change_pic_online(self, ctx: discord.Interaction, button: discord.ui.Button):
        try: await ctx.response.send_modal(menuPicModal(page=str(self.page + 1)))
        except Exception as e: print(e)

    # 改圖片(local)
    @discord.ui.button(
        label='改變圖片(local pic)',
        style = discord.ButtonStyle.gray,
        emoji="🥕"
    )
    async def change_pic_local(self, ctx: discord.Interaction, button: discord.ui.Button):
        try:
            await menuPicLocal(ctx, page=str(self.page + 1))
            if self.crt_msg: await ctx.delete_original_response()
            else: await self.crt_msg.delete()
            self.crt_msg = await ctx.followup.send(embed=embed_menu(str(self.page + 1)), view=self)
        except Exception as e:
            print(e)



    # 結束
    @discord.ui.button(
        label='掰',
        style = discord.ButtonStyle.red,
        emoji="🎣"
    )
    async def over(self, ctx: discord.Interaction, button: discord.ui.Button):
        if not self.crt_msg: self.ctx.delete_original_response()
        else: self.crt_msg.delete()

        
    
    async def on_timeout(self):
        print('FEWEN timeout le')
        await self.ctx.delete_original_response()



class ChiuChiuNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_today.before_loop(self.wait_until_7am)  # 先等待 7AM
        self.weather_today.start()  # 再啟動定時任務

    async def wait_until_7am(self, *_):
        """等待到下一個 7:00 AM 再開始執行"""
        now = datetime.now()
        target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)

        if now >= target_time:
            target_time += timedelta(days=1)  # 如果已經過了 7:00 AM，就等到明天

        wait_time = (target_time - now).total_seconds()
        print(f"🕖 等待 {wait_time / 3600:.2f} 小時，直到 7:00 AM 再執行天氣推送...")
        await asyncio.sleep(wait_time)

    @tasks.loop(hours=24)
    async def weather_today(self):
        """每天早上 7:00 AM 推送天氣消息"""
        await self.bot.wait_until_ready()  # 確保機器人已準備好
        channel = self.bot.get_channel(channelId)
        date = str(datetime.today().date())
        if channel:
            await channel.send(embed=discord.Embed(title=f'天氣預報 {date}', color=0x1b49de), view=weatherView(date))
            await channel.send(embed=discord.Embed(title=f'空氣品質 {date}', color=0x1bde83), view=airqualityView(date))      
            await channel.send(embed=discord.Embed(title=f'八卦新聞 {date}', color=0xebbf68), view=newsView(date))      
    
    # 天氣預報
    @app_commands.command(name = 'tianchiiii', description='878787')
    async def tianchiiii(self, ctx:discord.Interaction):
        embed = discord.Embed(
            title='天氣預報 ' + str(datetime.today().date()), 
            color=0x1b49de  
        )
        await ctx.response.send_message(embed=embed, view=weatherView(str(datetime.today().date())))
        
    # 空氣品質
    @app_commands.command(name = 'konchiiii', description='878787')
    async def konchiiii(self, ctx:discord.Interaction):
        embed = discord.Embed(
            title='空氣品質 ' + str(datetime.today().date()), 
            color=0x1bde83  
        )
        await ctx.response.send_message(embed=embed, view=airqualityView(str(datetime.today().date())))
        
    # 八卦新聞
    @app_commands.command(name='baguaaa', description='why u so baguaaa ahhh idiotttttt')
    async def baguaaa(self, ctx:discord.Interaction):
        
        embed = discord.Embed(
            title='最新八卦新聞 ' + str(datetime.today().date()),
            color=0xebbf68
        )
        await ctx.response.send_message(embed=embed, view=newsView(str(datetime.today().date())))
        
    # 菜單推送
    @app_commands.command(name="menuuu", description="miiii quick cook for meeeeeeee")
    async def menuuu(self, interaction: discord.Interaction): #, attachment: discord.Attachment):
        try:
            await interaction.response.send_message(embed=embed_menu(page="1"), view=menuEditView(ctx=interaction))
        except Exception as e:
            print(datetime.today().now(), e)
        """讓用戶一次上傳多張圖片，機器人回傳所有圖片
        if not attachment:
            await interaction.response.send_message("請至少上傳一張圖片！")
            return

        with open('/home/jeanthegod/chiubot/testing_cog/usefulma/carrot.json', 'r') as file:
            data = file

        image_urls = []
        for attachment in attachments:
            if attachment.content_type.startswith("image"):
                image_urls.append(attachment.url)
            else:
                print("⚠️ {attachment.filename} 不是圖片，已忽略。")

        if image_urls and len(image_urls) < 11:
            data['menu_pics'] = image_urls
        else:
            await interaction.response.send_message("❌ 沒有有效的圖片被上傳！")
            return"""

async def setup(bot):
    await bot.add_cog(ChiuChiuNews(bot))
