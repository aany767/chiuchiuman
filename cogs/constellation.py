import discord, asyncio, json, requests
from bs4 import BeautifulSoup
from discord.ext import commands
from discord import app_commands, SelectOption

class Constelletion_view(discord.ui.View):
    
    def __init__(self, ctx: discord.Interaction, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.stars = {
            0: "牡羊座", 1: "金牛座", 2: "雙子座", 3: "巨蟹座", 4: "獅子座", 5: "處女座",
            6: "天秤座", 7: "天蠍座", 8: "射手座", 9: "摩羯座", 10: "水瓶座", 11: "雙魚座"
        }

    @discord.ui.select(
        placeholder='ur constellation', 
        max_values=1,
        min_values=1,
        options = [
            SelectOption(label="牡羊座", value=0),
            SelectOption(label="金牛座", value=1),
            SelectOption(label="雙子座", value=2),
            SelectOption(label="巨蟹座", value=3),
            SelectOption(label="獅子座", value=4),
            SelectOption(label="處女座", value=5),
            SelectOption(label="天秤座", value=6),
            SelectOption(label="天蠍座", value=7),
            SelectOption(label="射手座", value=8),
            SelectOption(label="摩羯座", value=9),
            SelectOption(label="水瓶座", value=10),
            SelectOption(label="雙魚座", value=11),
            SelectOption(label='Over', value=12)
        ]
    )
    async def select_constellation(self, ctx: discord.Interaction, select: discord.ui.Select):
        value = int(select.values[0])
        if value == 12:
            embed = discord.Embed(
                title = 'WHY SO SHONNN',
                description = 'fufufufufufufu',
                color=0x94eaff  # Embed 顏色可以自行設置
            )
            await ctx.response.edit_message(content=None, embed=embed, view=None)
            return
            
        
        # 創建 STAR_FORTUNE 類的實例，然後調用 constellation 方法來獲得運勢資料
        star_fortune = STAR_FORTUNE()
        fortune_data = star_fortune.constellation(value)
        
        # 創建 Embed 來顯示運勢
        embed = discord.Embed(
            title=self.stars[value],  # 星座名稱作為 Embed 標題
            color=0x94eaff  # Embed 顏色
        )
        
        # 將運勢資料添加到 Embed 中
        for key, val in fortune_data.items():
            if '★' in val or '☆'  in key:
                embed.add_field(name=key, value=val, inline=False)
                embed.add_field(name='\u200b', value="\u200b", inline=False)
            else:
                embed.add_field(name=key, value=val, inline=True)
        

        # 更新訊息，顯示運勢
        await ctx.response.edit_message(content=None, embed=embed)

    async def on_timeout(self):
        print('constellation timeout le')
        await self.ctx.delete_original_response()
        
    
class STAR_FORTUNE():
    def __init__(self):
        self.url = 'https://astro.click108.com.tw/daily_{}.php?iAstro={}'
    
    def constellation(self, star: int):
        # 依照使用者所選星座生成對應網址並取的網頁原始碼
        self.url = self.url.format(star, star)
        data = requests.get(self.url)
        data.encoding = 'utf-8'
        data = BeautifulSoup(data.text, 'html.parser')
        # 處理星座資料並整理成字典
        lucky = data.find_all('div', class_='LUCKY')
        lucky = [str(i.text).replace('\n', '') for i in lucky]
        lucky = {
            '幸運數字' : lucky[0],
            '幸運顏色' : lucky[1],
            '開運方位' : lucky[2],
            '今日吉時' : lucky[3],
            '幸運星座' : lucky[4]    
        }
        today_content = data.find('div', class_='TODAY_CONTENT').text.split('\n')
        today_content = [i.split('：') for i in today_content][2:-1]
        for i in range(4):
            lucky[today_content[i][0]] = today_content[i][1]
        return lucky


class Constellation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # 星座運勢
    @app_commands.command(name='constellation_fortune', description='占卜lahhhhh')
    async def constellation_fortune(self, ctx: discord.Interaction):
        view = Constelletion_view(ctx=ctx)
        await ctx.response.send_message(content='wt is ur constellation?', view=view)
   
    
# 加载 Cog
async def setup(bot):
    await bot.add_cog(Constellation(bot))
