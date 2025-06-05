import discord, asyncio, json
from datetime import datetime
from discord.ext import commands
from discord import app_commands, SelectOption
from super import bugnovel, bugfortune, bugfewen

# 回傳時間戳
def get_timestamp():
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return timestamp_str

class findNovelView(discord.ui.View):
    def __init__(self, ctx, book_list):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.book_list = book_list
        self.select_book = discord.ui.Select(
            placeholder='Select a book',
            options=[
                SelectOption(label=f'{book[0]}', value=str(i)) for i, book in enumerate(self.book_list)
            ]
        )
        self.select_book.callback = self.select_callback
        self.add_item(self.select_book)

    
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        selected_book = self.book_list[int(select.values[0])]
        await interaction.response.send_message(f'Selected book: {selected_book[0]}')

class Flying_Gay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # __ is idiot        
    @app_commands.command(name='智障', description='who do u think is an idiot')
    async def idiot(self, ctx: discord.Interaction, name: str):
        try: 
            print(ctx.guild.members)
            await ctx.response.send_message(f'{name} is idiot')
        except Exception as e:
            print(e)

    # __ so colian    
    @app_commands.command(name='haha', description='u think who so colian and want to laugh')    
    async def haha(self, ctx: discord.Interaction, name: str):    
        await ctx.response.send_message(f'hahaha {name} so colian')   

    # __ 跟甲魚一樣8787
    @app_commands.command(name='甲魚', description='fishhh')
    async def fish(self, ctx: discord.Interaction, name: str):    
        await ctx.response.send_message(f'hahaha {name} 跟甲魚一樣8787')   

    # reminder    
    @app_commands.command(name='remindgay', description='this remind something a gay would like to know')
    async def remindgay(self, ctx: discord.Interaction, time_wait: int, text: str):
        try:
            await ctx.response.defer(thinking=False)
            await asyncio.sleep(time_wait)
            await ctx.followup.send(f'very important!!!   {text}   !!!')
        except Exception as e:
            await ctx.followup.send(f'Error: {e}')
            print(e)
     
    # 半夏小說   
    @app_commands.command(name='findnovel', description='u can use this to find a novel')
    @app_commands.describe(keyword = '你想找的小說類型 / 小說名')
    async def findnovel(self, ctx: discord.Interaction, keyword: str | None = '師尊'): 
        await ctx.response.send_message('This func is over, like ur life')
        '''
        async def too_many_words(content):
            if len(content) > 2000:
                # 如果内容超出 2000 字符，进行拆分
                chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
                for chunk in chunks:
                    await ctx.followup.send(chunk)
            else:
                await ctx.followup.send(content)
        
        # find books
        print(get_timestamp(), 'find book keyword')
        kkkkk = bugnovel.Banxia()
        #content, book_list = await asyncio.to_thread(kkkkk.find_book_names, keyword)
        content, book_list = kkkkk.find_book_names(keyword)
        print(get_timestamp(), 'find book keyword success')
        await ctx.response(f'Keyword: {keyword}')
        await ctx.followup.send(view=findNovelView(ctx, book_list))
        
        await ctx.followup.send('Which book do u want to read?\nreply in number ex: 3')
        
        
            
              
        def check(m):
            return  m.author == ctx.user and m.channel == ctx.channel
            
        try:
            msg = await self.bot.wait_for('message', timeout=300.0, check=check)
        except asyncio.TimeoutError as e:
                print(e)
                await ctx.followup.send('U answer too slow u idiot')
                await ctx.followup.send('u useless people ')
                return
        else:
            kkkkk.url, book_name = book_list[int(msg.content) - 1][1], book_list[int(msg.content) - 1][0]
        
        titles, title_links = kkkkk.main()
        await ctx.followup.send(f'Book Name: {book_name}')
        await too_many_words(titles)
        
            
        while 1:        
            await ctx.followup.send('Which title do u want to read?\ntell me the chapter ex: 5\nif u dont want to read anymore then type in u too chiu')
                
            try:
                msg = await self.bot.wait_for('message', timeout=3000.0, check=check)
            except asyncio.TimeoutError:
                await ctx.followup.send('U answer too slow u idiot')
                await ctx.followup.send('u useless people ')
                return
            else:
                if msg.content == 'u too chiu': break
                
                kkkkk.url, title_name = title_links[int(msg.content) - 1][1], title_links[int(msg.content) - 1][0]
                content = kkkkk.page()
                await ctx.followup.send(f'Book Name: {book_name}\nTitle: {title_name}')
                await too_many_words(content)
                    
        await ctx.followup.send('over')
        
        return'''

    # 是否是管理員
    @app_commands.command(name="is_admin", description='see if u r an admin')
    async def is_admin(self, ctx: discord.Interaction):
        try:
            if ctx.user.guild_permissions.administrator:
                await ctx.response.send_message(f"{ctx.user.mention} 是管理員！")
            else:
                await ctx.response.send_message(f"{ctx.user.mention} 不是管理員。")
        except Exception as e:
            print(e)

    # 彩虹
    @app_commands.command(name='rainbow', description='我是彩虹hehehehe')
    async def rainbow(self, ctx: discord.Interaction):
    
        a = [
        0xFF0000,  # Red
        0xFF1A00,  # Light Red
        0xFF3300,  # Orange Red
        0xFF4D00,  # Orange
        0xFF6600,  # Dark Orange
        0xFF8000,  # Yellow Orange
        0xFF9900,  # Light Orange
        0xFFB300,  # Amber
        0xFFCC00,  # Gold
        0xFFFF00,  # Yellow
        0xB2FF00,  # Yellow Green
        0x80FF00,  # Chartreuse
        0x4DFF00,  # Green Yellow
        0x00FF00,  # Green
        0x00E600,  # Lime Green
        0x00CC00,  # Dark Green
        0x00B300,  # Forest Green
        0x009900,  # Dark Olive Green
        0x006600,  # Very Dark Green
        0x003300,  # Darkest Green
        0x0000FF,  # Blue
        0x0033FF,  # Light Blue
        0x0066FF,  # Sky Blue
        0x3399FF,  # Deep Sky Blue
        0x66CCFF,  # Light Sky Blue
        0x99CCFF,  # Light Blue (Light)
        0x66B2FF,  # Medium Light Blue
        0x3399FF,  # Deep Sky Blue
        0x0000CC,  # Royal Blue
        0x0000B3,  # Dark Blue
        0x000099,  # Navy
        0x8A2BE2,  # Blue Violet
        0x9400D3,  # Dark Violet
        0x9932CC,  # Dark Orchid
        0x8B008B,  # Dark Magenta
        0x800080,  # Purple
        0x8A2BE2,  # Blue Violet
        0x9400D3,  # Dark Violet
        0x9B30FF,  # Purple Blue
        0x9932CC,  # Dark Orchid
        0x8B008B,  # Dark Magenta
        0x800080,  # Purple
        0x7A006A,  # Purple Red
        0x800040,  # Magenta
        0xFF00FF,  # Magenta (Fuchsia)
        0xD200D2,  # Purple Pink
        0xD700FF,  # Violet
        0xE600E6,  # Fuchsia
        0xFF1493,  # Deep Pink
        0xFF007F,  # Hot Pink
        0xFF0000,  # Red (back to start)
    ]
        
        embed = discord.Embed(
            title='RAINBOW',
            description='AB is gayyyyyy！！！',
            color=a[0]
        )

        # 发送初始消息并获取引用
        await ctx.response.defer(thinking=False)
        message = await ctx.followup.send(embed=embed)
        for _ in range(3):
            for color in a:
                await asyncio.sleep(0.01)  
                embed.color = color
                await message.edit(embed=embed)
    
    # 星座運勢
    @app_commands.command(name='constellation_fortune', description='占卜lahhhhh')
    async def constellation_fortune(self, ctx: discord.Interaction):
        view = bugfortune.Constelletion_view(ctx=ctx)
        await ctx.response.send_message(content='wt is ur constellation?', view=view)

    # 廢文產生器
    @app_commands.command(name='fewen_generater', description='廢文產生器')
    @app_commands.describe(
        topic_value = '主題',
        char_value = '字數 (100~10000)',
        para_value = '段落數 (1~1000)'
    )
    async def fewen_generater(self, ctx: discord.Interaction, topic_value: str | None = '邱', char_value: int | None = 100, para_value: int | None = 1):
        await ctx.response.defer(thinking=True)
        paras = bugfewen.FEWEN().generate_fewen(topic_value=topic_value, char_value=char_value, para_value=para_value) 
        para = bugfewen.FEWEN().deal_with_fewen(paras[0]) + [paras[1][:-6] + paras[1][-1]]
        view = bugfewen.Fewen_View(ctx=ctx, topic_value=topic_value, data=para)
        
        embed = discord.Embed(
            title=topic_value,
            description= para[0],
            color=discord.Color.from_rgb(112, 230, 201)
        )
        embed.add_field(name='\u200b', value=f'第1頁')
        await ctx.followup.send(embed=embed, view=view)
        
        
    # 邀請紅蘿蔔傑克
    @app_commands.command(name='carrot_invite', description='i love carrot jackkkk')
    async def carrot_invite(self, ctx: discord.Interaction):
        path = '/home/jeanthegod/chiubot/testing_cog/usefulma/carrot.json'
        id = str(ctx.channel_id)
        with open(path, 'r') as file:
            data = json.load(file)
        
        if id in data['carrot']: 
            await ctx.response.send_message('carrot jack is already in this channel')
            return
        
        data['carrot'].append(id)
        
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
        await ctx.response.send_message(f'Carrot Jack is now invited to channel{ctx.channel.name}')
        
    # 踢出踢出紅蘿蔔傑克
    @app_commands.command(name='carrot_kick', description='i hate carrot jackkkk')
    async def carrot_kick(self, ctx: discord.Interaction):
        path = '/home/jeanthegod/chiubot/testing_cog/usefulma/carrot.json'
        id = str(ctx.channel_id)
        with open(path, 'r') as file:
            data = json.load(file)
    
        if id not in data['carrot']: 
            await ctx.response.send_message('carrot jack is not in this channel lahhh, idiot')
            return
        
        data['carrot'].remove(id)
        
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
        await ctx.response.send_message(f'Carrot Jack is now kick from channel{ctx.channel.name}')
     
    # 紅蘿蔔傑克在哪裡
    @app_commands.command(name='carrot_where', description='where is carrot jackkkk')
    async def carrot_where(self, ctx: discord.Interaction):
        try:
            path = '/home/jeanthegod/chiubot/testing_cog/usefulma/carrot.json'
            yes = []
            no = []
            embed = discord.Embed(
                title='紅蘿蔔傑克在哪裡~~~',
                description=ctx.guild.name
            )
            with open(path, 'r') as file: data = json.load(file)['carrot']
            
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.CategoryChannel): continue
                if str(channel.id) in data: yes.append(str(channel.id))
                else: no.append(str(channel.id))
             
            a, b = '', ''   
            
            # 檢查是否有頻道包含紅蘿蔔傑克
            if not yes:
                a += "沒有人愛紅蘿蔔傑克QQ\n"
            else:
                for channel_id in yes:
                    a += f"<#{channel_id}>     "
                    
            if not no:
                b += "大家都愛紅蘿蔔傑克！哇哇！❤️❤️❤️"
            else:
                for channel_id in no:
                    b += f"<#{channel_id}>     "
                   
            embed.add_field(name='紅蘿蔔傑克在~~~', value=a, inline=False)  
            embed.add_field(name='紅蘿蔔傑克不在~~~', value=b, inline=False)
            await ctx.response.send_message(embed=embed)
        except Exception as e:
            print(e)
    
    
    
# 加载 Cog
async def setup(bot):
    await bot.add_cog(Flying_Gay(bot))
