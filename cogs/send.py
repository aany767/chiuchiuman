# 此檔案請修改第 16 行 #

import discord 
from discord.ext import commands, tasks
import json
import datetime
import asyncio
import pytz

def get_time():
    taiwan_tz = pytz.timezone("Asia/Taipei")
    t = datetime.datetime.now(pytz.UTC).astimezone(taiwan_tz)
    t = t.replace(tzinfo=None)
    return t

json_file = "REMIND_JSON_FILE_PATH"  # Replace with your actual JSON file path

class send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file = json_file
        self.check_scheduled_messages.start()

    def cog_unload(self):
        self.check_scheduled_messages.cancel()


    @tasks.loop(seconds=5) 
    async def check_scheduled_messages(self):
        self.json_file = json_file
        #print('hi')
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                #print('messages:', messages)

        
        except Exception as e:
            print(e)
            return
        try:
            
            current_time = get_time()
            
            for msg_id, msg_data in messages.items():

                if msg_data['done'] == True:

                    scheduled_time = datetime.datetime.strptime(
                        msg_data["time"], "%Y-%m-%d %H:%M:%S"
                    )

                    if current_time >= scheduled_time:
                        channel = self.bot.get_channel(int(msg_data["channel"]))
                        #print('channel:', channel)

                        if channel:
                            print(f'[{str(get_time()).split(".")[0]}] sending num {msg_id} to {channel}')

                            embed = discord.Embed(
                                title=msg_data["title"],
                                description=msg_data["description"],
                                color=discord.Color.blue()
                            )
                            embed.set_image(url=msg_data["image"])

                            try:
                                await channel.send(embed=embed)

                                if msg_data["interval"] == None:
                                    del messages[msg_id]
                                    with open(self.json_file, 'w', encoding='utf-8') as f:
                                        json.dump(messages, f, indent=4, ensure_ascii=False)
                                else:
                                    # 計算下一次發送時間
                                    interval = msg_data["interval"]
                                    time_delta = datetime.timedelta(
                                        days=interval["days"],
                                        hours=interval["hours"],
                                        minutes=interval["minutes"],
                                        seconds=interval["seconds"]
                                    )
                                    
                                    # 更新下一次的發送時間
                                    new_time = scheduled_time + time_delta
                                    messages[msg_id]["time"] = new_time.strftime("%Y-%m-%d %H:%M:%S")
                        
                                    with open(self.json_file, 'w', encoding='utf-8') as f:
                                        json.dump(messages, f, indent=4, ensure_ascii=False)
                                    
                            except discord.errors.Forbidden:
                                print(f"沒有權限在 {msg_data['channel']} 發送訊息")
                            except Exception as e:
                                print(e)

        except Exception as e:
            print(e)
                        
                    
                        
'''
    @check_scheduled_messages.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()'''


async def setup(bot):
    await bot.add_cog(send(bot))