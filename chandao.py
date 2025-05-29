import discord, json, pytz, os, asyncio
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from discord import SelectOption

path = '/home/jeanthegod/chiubot/testing_cog/usefulma/chandao_members.json'

def how_many_days(year, month):
    big_months = [1, 3, 5, 7, 8, 10, 12]
    small_months=[4, 6, 9, 11]
    is_ren_nian = 0                
    if year%4 == 0: is_ren_nian = 1           
    if year%100 == 0: is_ren_nian = 0          
    if year%400 == 0: is_ren_nian = 1 
    if month in big_months: return 31
    if month in small_months: return 30
    if is_ren_nian: return 29
    return 28
# View 簽到
class Sign(discord.ui.View):
    def __init__(self, ctx: discord.Interaction, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.embed = discord.Embed(title="簽到", description="balalalala", color=0x94eaff)

    def update_chandao_lists(self, ctx):
        """更新簽到和未簽到名單"""
        current_date = datetime.now().date().isoformat()
        name = ctx.user.nick if ctx.user.nick else ctx.user.name
        with open(path, 'r') as file:
            data = json.load(file)
        user_id = str(ctx.user.id)
        
        # 檢查今天的簽到狀態
        if current_date not in data["user"]:
            data["user"][current_date] = {}

        if user_id not in data["user"][current_date]:
            # 若用戶尚未簽到，進行簽到
            data["user"][current_date][user_id] = {
                "name":name,
                "status": "yes",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(name, 'sign in!', current_date)
            self.embed.description = f"{name} sign in！"
        
        else:
            # 用戶已經簽到
            self.embed.description = f"{name} You have already signed in ！"
            
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
     
    def cancel_chandao_lists(self, ctx):
        """更新簽到和未簽到名單"""
        current_date = datetime.now().date().isoformat()
        name = ctx.user.nick if ctx.user.nick else ctx.user.name
        with open(path, 'r') as file:
            data = json.load(file)
        user_id = str(ctx.user.id)
        
        # 檢查今天的簽到狀態
        if current_date not in data["user"]:
            data["user"][current_date] = {}

        if user_id not in data["user"][current_date]:
            # 若用戶尚未簽到， 罵他
            self.embed.description = f'{name} you 都還沒簽到過是在取消個屁'
        
        else:
            # 用戶已經簽到
            del data["user"][current_date][user_id]
            print(name, 'cancel sign in!', current_date)
            self.embed.description = f"{name} is an idiot"
            self.embed.description = f"{name} why u cancel lah wuwuwuwu"
            
        with open(path, 'w') as file:
            json.dump(data, file, indent=4) 
     
        
    @discord.ui.button(
        label="yes", 
        emoji='⭕',
        style=discord.ButtonStyle.green
    )
    async def button_one(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.update_chandao_lists(ctx)
        
        await ctx.response.edit_message(content=None, embed=self.embed, view=None)

    @discord.ui.button(
        label="取消之前簽到", 
        emoji='💩',
        style=discord.ButtonStyle.grey
    )
    async def cancel_chandao(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.cancel_chandao_lists(ctx)
        
        await ctx.response.edit_message(content=None, embed=self.embed, view=None)

    @discord.ui.button(
        label="no", 
        emoji='🙅‍♂️',
        style=discord.ButtonStyle.red
    )
    async def button_two(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.embed.description = "cancel❌"
        await ctx.response.edit_message(content=None, embed=self.embed, view=None)

    async def on_timeout(self):
        print('chandaooo timeout le')
        await self.ctx.delete_original_response()
# View 簽到記錄
class Check_Sign(discord.ui.View):
    def __init__(self, ctx: discord.Interaction, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.embed = discord.Embed(title=" sign in sheet", description="", color=0x94eaff)
        self.ctx = ctx
        self.view_or_back = 0
    
    def check_chandao_lists(self, ctx):
        """check簽到和未簽到名單"""
        current_date = datetime.now().date().isoformat()
        name = ctx.user.nick if ctx.user.nick else ctx.user.name
        
        with open(path, 'r') as file:
            data = json.load(file)
        
        members = [str(i.id) for i in ctx.guild.members if not i.bot]
        
        self.embed.title = 'sign in sheet' + current_date
       
        self.embed.add_field(name='Yes', value="\u200b", inline=False)
        for user in data['user'][current_date]:
            if user not in members: continue
            members.remove(user)
            self.embed.add_field(
                name=data['user'][current_date][user]["name"], 
                value=f'<@{int(user)}>',
                inline=True)
         
        if data['user'][current_date] == {}:
            self.embed.add_field(name='no worker', value='')    
            
        self.embed.add_field(name='\u200b', value='\u200b', inline=False)
        self.embed.add_field(name='No', value='\u200b', inline=False)
        
        
        for user_id in members:
            user = ctx.guild.get_member(int(user_id))   
            self.embed.add_field(
                name=user.nick if user.nick else user.name, 
                value=f'<@{int(user_id)}>',
                inline=True)
        
        if not members:
            self.embed.add_field(name='no one sign in', value='')
            
    
    @discord.ui.button(
        label='check who have signed', 
        emoji='✅', 
        style=discord.ButtonStyle.danger
    )
    async def check_chandao_today(self, ctx: discord.Interaction, button: discord.ui.Button):
        if self.view_or_back % 2 == 0:
            self.view_or_back += 1
            self.embed.clear_fields()

            # 更新簽到清單
            self.check_chandao_lists(ctx)
           

            self.embed.description = 'who have sign in'
            button.label = 'return'
            button.style = discord.ButtonStyle.gray
            await ctx.response.edit_message(content=None, embed=self.embed, view=self)
        else:
            self.view_or_back += 1
            button.label = 'check who have signed'
            button.style = discord.ButtonStyle.danger
            self.embed.clear_fields()
            self.embed.title = 'Today is a nice day !'
            self.embed.description = 'fighting !'
            await ctx.response.edit_message(content=None, embed=self.embed, view=self)

    @discord.ui.button(
        label='month', 
        emoji='🙄', 
        style=discord.ButtonStyle.green
    )
    async def check_chandao_by_month(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.embed.clear_fields()
        await ctx.response.send_modal(Sign_Modal_By_Month())
        
    @discord.ui.button(
        label='day', 
        emoji='😭', 
        style=discord.ButtonStyle.blurple
    )
    async def check_chandao_by_day(self, ctx: discord.Interaction, button: discord.ui.Button):
        self.embed.clear_fields()
        await ctx.response.send_modal(Sign_Modal_By_Day())
        
            
        
        

    async def on_timeout(self):
        print('list_chandaooo timeout le')
        await self.ctx.delete_original_response()
# Modal 依月份
class Sign_Modal_By_Month(discord.ui.Modal, title='欲查詢月份'):
    def __init__(self):
        super().__init__(timeout = 180)
        self.embed = discord.Embed(title="sign in sheet", description="", color=0x94eaff)
        self.year = discord.ui.TextInput(label='which year - yyyy', placeholder=str(datetime.now().year), max_length=4, min_length=4)
        self.month = discord.ui.TextInput(label='which month - mm', placeholder=str(datetime.now().month), min_length=1, max_length=2)
        self.add_item(self.year)
        self.add_item(self.month)
    
    def find_month(self, wanted_year, wanted_month):
        with open(path, 'r') as file:
            data = json.load(file)
        chandao_list_that_day = {i:{} for i in range(1, how_many_days(wanted_year, wanted_month))}
        if wanted_year == datetime.now().year and wanted_month == datetime.now().month: 
            chandao_list_that_day = {i:{} for i in range(1, datetime.today().day + 1)}
        for date in data['user']:
            year, month, day = [int(i) for i in date.split('-')]
            if not (year==wanted_year and month==wanted_month): continue
            for id in data['user'][date]:
                chandao_list_that_day[day][id] = data['user'][date][id]
        return chandao_list_that_day
       
    async def on_submit(self, ctx: discord.Interaction):
        try:
            try:
                year = int(self.year.value)
                month = int(self.month.value)
            except:
                self.embed.title = '輸入格式錯誤'
                await ctx.response.edit_message(embed=self.embed)
                
            current_year = datetime.now().year
            current_month = datetime.now().month
            if year > current_year or (year == current_year and month > current_month):
                self.embed.title = '啊你是在未來簽到了喔?\n給我重填啦傻逼'
                await ctx.response.edit_message(embed=self.embed)
            elif month > 12 or month < 1:
                self.embed.title = '你連一年幾個月都不知道嗎?\nwhy so idiottttt'
                await ctx.response.edit_message(embed = self.embed)
            else:
                chandao_list_by_month = self.find_month(year, month)
                self.embed.title = 'chandao p by month ohhhh'
                self.embed.clear_fields()
                members = [str(i.id) for i in ctx.guild.members if not i.bot]
                text = ''
                text_month, text_ppl = '', ''
                for day in chandao_list_by_month:
                    ids = []
                    for id in chandao_list_by_month[day]:
                        if id not in members: continue
                        ids.append( f'<@{int(id)}>')
                    text_month += f'{month}/{day}\n\n'
                    text_ppl += f"{' '.join(ids)}\n\n" if ids else 'no one 87\n\n'
                    #text += f'**{month}/{day}**'.ljust(10, "　") + ' '.join(ids) + '\n\n' if ids else f'**{month}/{day}**'.ljust(10, '　') + 'wuwuwu no one lahh fufufu\n\n'
                #self.embed.description = text
                self.embed.add_field(name='日期', value=text_month.strip())
                self.embed.add_field(name='簽到人員', value=text_ppl.strip())
                await ctx.response.edit_message(embed=self.embed)
        except Exception as e:
            print(e)
# Modal 依日期
class Sign_Modal_By_Day(discord.ui.Modal, title='欲查詢日期'):
    def __init__(self):
        super().__init__(timeout = 180)
        self.embed = discord.Embed(title="sign in sheet", description="", color=0x94eaff)
        self.year = discord.ui.TextInput(label='which year - yyyy', placeholder=str(datetime.now().year), max_length=4, min_length=4)
        self.month = discord.ui.TextInput(label='which month?', placeholder=str(datetime.now().month), min_length=1, max_length=2)
        self.day = discord.ui.TextInput(label='which day?', placeholder=datetime.today().day, min_length=1, max_length=2)
        self.add_item(self.year)
        self.add_item(self.month)
        self.add_item(self.day)
    
    def find_day(self, wanted_year, wanted_month, wanted_day):
        with open(path, 'r') as file:
            data = json.load(file)
        chandao_list_that_day = {}
        for date in data['user']:
            year, month, day = [int(i) for i in date.split('-')]
            if not (year==wanted_year and month==wanted_month and day == wanted_day): continue
            for id in data['user'][date]:
                chandao_list_that_day[id] = data['user'][date][id]
        print(chandao_list_that_day)
        return chandao_list_that_day
       
    async def on_submit(self, ctx: discord.Interaction):
        try:
            try:
                year = int(self.year.value)
                month = int(self.month.value)
                day = int(self.day.value)
            except:
                self.embed.title = '輸入格式錯誤'
                await ctx.response.edit_message(embed=self.embed) 
                
            current_year = datetime.now().year
            current_month = datetime.now().month
            current_day = datetime.today().day
            if year > current_year or (year == current_year and month > current_month) or (year == current_year and month == current_month and day > current_day):
                self.embed.title = '啊你是在未來簽到了喔?\n給我重填啦傻逼'
                await ctx.response.edit_message(embed=self.embed)
            elif month > 12 or month < 1:
                self.embed.title = '你連一年幾個月都不知道嗎?\nwhy so idiottttt'
                await ctx.response.edit_message(embed = self.embed)
            elif day < 1 or day > how_many_days(year, month):
                self.embed.title = '你連一個月幾天都不知道嗎?\nwhy so idiottttt'
                await ctx.response.edit_message(embed = self.embed)
            else:
                chandao_list_by_day = self.find_day(year, month, day)
                self.embed.title = f'chandao p {year}-{month}-{day}'
                self.embed.clear_fields()
                members = [str(i.id) for i in ctx.guild.members if not i.bot]
            
                if not chandao_list_by_day: 
                    self.embed.description  = 'fufufufufu no one chandaooooooo'
                    await ctx.response.edit_message(embed=self.embed)
                t_ppl = ''
                for id in chandao_list_by_day:
                    if id not in members: continue
                    t_ppl += f'<@{id}>\n\n' 
                self.embed.add_field(name='簽到人員', value=t_ppl.strip())
                await ctx.response.edit_message(embed=self.embed)
        except Exception as e:
            print(e)

class Chandao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.initialize_data()
        self.reset_sign_data.start()

    # 檢查並初始化資料檔案
    def initialize_data(self):
        if not os.path.exists(path):
            # 若檔案不存在，初始化資料結構
            data = {
                "user": {},
                "last_reset": None
            }
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
        else:
            with open(path, 'r') as file:
                data = json.load(file)
                if 'last_reset' not in data or data['last_reset'] is None:
                    data['last_reset'] = datetime.now().date().isoformat()
                    with open(path, 'w') as file:
                        json.dump(data, file, indent=4)

    # 每天自動記錄簽到資料
    @tasks.loop(hours=24)
    async def reset_sign_data(self):
        # 每天檢查並更新簽到資料
        current_date = datetime.now().date().isoformat()
        with open(path, 'r') as file:
            data = json.load(file)
        
        # 確保每天的資料紀錄存在
        if current_date not in data["user"]:
            data["user"][current_date] = {}

        # 更新檔案
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)


    # 簽到
    @app_commands.command(name="sign_in", description="hello")
    async def sign_in(self, ctx: discord.Interaction):
        await ctx.response.send_message(content="Are you sure you want to sign in?", view=Sign(ctx=ctx))
    # 簽到名單  
    @app_commands.command(name='sign_in_sheet', description='who is working?')
    async def sign_in_sheet(self, ctx: discord.Interaction):
        await ctx.response.send_message(view=Check_Sign(ctx=ctx))

   

async def setup(bot):
    await bot.add_cog(Chandao(bot))






