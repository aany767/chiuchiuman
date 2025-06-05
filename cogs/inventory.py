import discord, asyncio, requests, random, json, validators, mysql.connector, os, gspread
from google.oauth2.service_account import Credentials
from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord import app_commands, SelectOption
from typing import List
from discord.ui import TextInput
global_original_item_url = 'ur sheet url'
global_original_log_url = 'ur sheet url'
global_font_path = 'FONTS/SARASAMONOCL-REGULAR.TTF' #可換成自己的字體路徑
global_cred_path = 'JSON/credentials.json' # 需換上自己的憑證
global_sheet_guide_path = 'IMAGES/sheetGuide.jpg' # 可換成自己的圖片

# 回傳時間戳
def get_timestamp():
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return timestamp_str
# 回傳美麗的倉庫表格 (圖片)
def show_table(data: list, ctx: discord.Interaction, ItemOrLog: str, text: str):
    if ItemOrLog == 'items': columns = ['item_id', 'name', 'category', 'unit', 'quantity', 'threshold', 'last_update']
    else: columns = ['log_id', 'item_id', 'change_amount', 'timestamp', 'note']
    table = PrettyTable()
    table.field_names = columns
    for i in data:
        table.add_row(i)
    table.align = 'l' # 向左靠
    table_str = str(table)

    # 2. 載入中文字型（等寬，適合表格）
    font_path = global_font_path # 全等距
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)

    # 3. 計算圖片尺寸
    lines = table_str.split('\n')
    padding = 20
    line_height = font.getbbox("測")[3] + 6
    width = int(max(font.getlength(line) for line in lines)) + padding * 2
    height = line_height * (len(lines) + 1) + padding * 2

    bg = Image.new(mode='RGBA',size=(width, height), color=(55, 69, 53, 255)) # 背景顏色
    
    # 6. 開始畫圖
    draw = ImageDraw.Draw(bg)
    y = padding
    draw.text((padding, y), f'[倉庫] {ctx.guild.name} - {text}', font=font, fill=(204, 180, 101, 255)) # 標題顏色
    
    y = padding + line_height
    for line in lines:
        draw.text((padding, y), line, font=font, fill=(174, 169, 118, 255)) # 表格顏色
        y += line_height

    # 7. 存到記憶體並傳送
    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="inventory.png")
    return file
 
# Sheet 更新倉庫
def sheet_update_item(ctx: discord.Interaction, url: str | None):
    item_url = url if url else  global_original_item_url
    
    
    server_id = str(ctx.guild.id)
    credPath = global_cred_path
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds =Credentials.from_service_account_file(credPath, scopes=scopes)
    client = gspread.authorize(creds)
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    item_workbook = client.open_by_url(item_url)
    items = select_inventory_item_all_for_sheet(server_id=server_id, ItemOrLog='items')
    itemSheetList = list(map(lambda x: x.title, item_workbook.worksheets()))
    sheet_name = 'inventory_items_' + server_id
    if sheet_name in itemSheetList: itemSheet = item_workbook.worksheet(sheet_name)
    else: itemSheet = item_workbook.add_worksheet(sheet_name, rows=len(items) + 1, cols=len(items[0]))
    itemSheet.clear()
    itemSheet.update_acell('A1', value='[倉庫] '+ctx.guild.name)
    itemSheet.format('A1', {'textFormat': {'bold' : True, 'italic': True}})
    itemSheet.update(f'a2:{alphabet[len(items[0])]}{len(items) + 1}', items)
# Sheet 更新倉庫紀錄
def sheet_update_log(ctx: discord.Interaction, url: str | None):
    log_url = url if url else global_original_log_url
    
    server_id = str(ctx.guild.id)
    credPath = global_cred_path
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds =Credentials.from_service_account_file(credPath, scopes=scopes)
    client = gspread.authorize(creds)
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    
    log_workbook = client.open_by_url(log_url)
    logs = select_inventory_item_all_for_sheet(server_id, ItemOrLog='logs')
    logSheetList = list(map(lambda x: x.title, log_workbook.worksheets()))
    sheet_name = 'inventory_logs_' + server_id
    if sheet_name in logSheetList: logSheet = log_workbook.worksheet(sheet_name)
    else: logSheet = log_workbook.add_worksheet(sheet_name, rows=len(logs) + 1, cols=len(logs[0]))
    logSheet.clear()
    logSheet.update_acell('A1', value='[倉庫紀錄] '+ctx.guild.name)
    logSheet.format('A1', {'textFormat': {'bold' : True, 'italic': True}})
    logSheet.update(f'a2:{alphabet[len(logs[0])]}{len(logs) + 1}', logs)

 
# SQL 建立連線 
def get_connection():
    return mysql.connector.connect(
        host = 'localhost',
        port = '3306',
        user = 'user',
        password = 'password',
        database = 'ur database'
    )   
# SQL 該伺服器是否 in servers
def is_server_exist(server_id):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('select server_id from servers;')
    data = [i[0] for i in cursor.fetchall()]
    if server_id in data: return True
    return False
# SQL 新增伺服器到 servers
def add_server(server_id, server_name: str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('insert into servers (server_id, server_name) values (%s, %s);', (server_id, server_name))
    connection.commit()
    cursor.close()
    print(f'[{get_timestamp()}] - add server {server_id} to servers')
# SQL 更新伺服器 sheet url
def update_server_sheet_url(server_id, item_url: str, log_url: str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    item_url = item_url if item_url else global_original_item_url
    log_url = log_url if log_url else global_original_log_url
    cursor.execute('update servers set item_url = %s, log_url = %s where server_id = %s;', (item_url, log_url, server_id))
    connection.commit()
    cursor.close()
    print(f'[{get_timestamp()}] - update server {server_id} sheet url')
# SQL 查詢伺服器 sheet url
def select_server_sheet_url(server_id):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('select item_url, log_url from servers where server_id = %s;', (server_id,))
    data = cursor.fetchall()
    cursor.close()
    if data: return data[0]
    return None, None
# SQL 創建table    
def create_new_tables(server_id):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    # create 倉庫 table
    cursor.execute(f'''
        create table inventory_items_{server_id}(
        item_id int auto_increment primary key,
        `name` varchar(30) unique not null,
        category varchar(30) default null,
        unit varchar(20) default '單位',
        quantity int default 0,
        threshold int default 0,
        last_update timestamp default current_timestamp on update current_timestamp
    );
    ''')
    # create 倉庫紀錄 table
    cursor.execute(f'''
        create table inventory_logs_{server_id}(
        log_id int auto_increment primary key,
        item_id int not null,
        change_amount int default 0,
        `timestamp` timestamp default current_timestamp,
        note varchar(50) default null,
        FOREIGN KEY (item_id) REFERENCES inventory_items_{server_id}(item_id) ON DELETE CASCADE
    );               
    ''')
    cursor.close()
# SQL 該伺服器是否有table
def is_table_exist(server_id):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('show tables;')
    tables = [i[0] for i in cursor.fetchall()]
    if f'inventory_items_{server_id}' in tables: return True
    return False
# SQL 查看倉庫品項 [column] only
def select_inventory_item_by_column(server_id, column: str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        f'''select {column} from inventory_items_{server_id};'''
    )
    names = [i[0] for i in cursor.fetchall()]
    cursor.close()
    return names
# SQL 查看倉庫 all
def select_inventory_item_all(server_id, ItemOrLog:str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f'select * from inventory_{ItemOrLog}_{server_id};')
    data = cursor.fetchall()
    cursor.close()
    data = [list(row[:-1]) + [str(row[-1])] for row in data]
    return data
# SQL 查看倉庫 all for Sheet
def select_inventory_item_all_for_sheet(server_id, ItemOrLog:str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'inventory_{ItemOrLog}_{server_id}'")# AND TABLE_SCHEMA = '你的数据库名'")
    columns = [row[0] for row in cursor.fetchall()]
    cursor.execute(f'select * from inventory_{ItemOrLog}_{server_id};')
    data = cursor.fetchall()
    cursor.close()
    if ItemOrLog == 'items': data = [list(row[:-1]) + [str(row[-1])] for row in data]
    else: 
        data = [list(row[:-2]) + [str(row[-2])] + [row[-1]] for row in data]
    data = [columns] + data
    
    return data
# SQL 查看倉庫 安全
def select_inventory_item_safety(server_id):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f'select * from inventory_items_{server_id} where quantity < threshold;')
    data = cursor.fetchall()
    cursor.close()
    data = [list(row[:-1]) + [str(row[-1])] for row in data]
    return data
# SQL 搜尋倉庫品項
def search_inventory_item(server_id, name: str | None, category: str | None, unit: str | None):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    name = f"'%{name}%'" if name else 'name'
    category = f"'%{category}%'" if category else 'category'
    unit = f"'%{unit}%'" if unit else 'unit'
    cursor.execute(f'''
        select * from inventory_items_{server_id}
        where name like {name} and category like {category} and unit like {unit};
    ''')
    data = cursor.fetchall()
    cursor.close()
    data = [list(row[:-1]) + [str(row[-1])] for row in data]
    return data 
# SQL 增加倉庫品項
def add_inventory_item_table(server_id, name: str, category: str | None, unit: str | None, quantity: int | None, threshold: int | None):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f'''
        INSERT INTO inventory_items_{server_id}
        (`name`, category, unit, quantity, threshold)
        VALUES (%s, %s, %s, %s, %s);
    ''', (
        name,
        category if category else None,
        unit if unit else '單位',
        quantity if quantity else 0,
        threshold if threshold else 0
    ))
    print(f'[{get_timestamp()}] - inventory column added - name: {name}  \
        category: {category}  \
        unit: {unit}  \
        quantity: {quantity}  \
        threshold: {threshold}')
    
    # 🔥 這裡要加上 commit()，才會真的儲存到資料庫
    connection.commit()  
    cursor.close()
# SQL 刪除倉庫品項
def delete_inventory_item_table(server_id, name: str, item_id: str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    name = f"'{name}'" if name else 'name'
    item_id = item_id if item_id != '' else 'item_id'
    cursor.execute(f"DELETE FROM inventory_items_{server_id} WHERE name = {name} and item_id = {item_id};")
    connection.commit()
    cursor.close()
    print(f'[{get_timestamp()}] - inventory delete column - name:{name}  item_id: {item_id}')
# SQL 更新倉庫
def update_inventory_item_table(server_id, item_id: int, change_amount: int, note: str):
    server_id = str(server_id)
    connection = get_connection()
    cursor = connection.cursor()
    # 添加倉庫紀錄
    cursor.execute(f'''
        insert into inventory_logs_{server_id}
        (item_id, change_amount, note)
        values
        ({item_id}, {change_amount}, '{note}');''')
    # 改倉庫物品數量
    cursor.execute(f'''
        update inventory_items_{server_id}
        set quantity = {change_amount} + quantity
        where item_id = {item_id};''')
    connection.commit()
    cursor.close()
    print(f'[{get_timestamp()}] - inventory log add column -  item_id: {item_id}, change_amount: {change_amount}, note: {note}')


# Modal 增加品項
class addItemModal(discord.ui.Modal, title = '增加品項'):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout = 180)
        self.embed = embed
        self.name= TextInput(label='名稱', placeholder='Mia is poo', max_length=30, min_length=1)
        self.category = TextInput(label='種類', placeholder='ex: 肉類, 蔬菜', max_length=30, required=False)
        self.unit = TextInput(label='單位', placeholder='ex: 個, 公斤', max_length=20, min_length=1, required=False)
        self.quantity = TextInput(label='數量', placeholder='ex: 1, 23, 45', max_length=10, required=False)
        self.threshold = TextInput(label='最低安全數量', placeholder='ex: 87, 174, 8787', max_length=10, required=False)
        self.add_item(self.name)
        self.add_item(self.category)
        self.add_item(self.unit)
        self.add_item(self.quantity)
        self.add_item(self.threshold)
    
    async def on_submit(self, ctx: discord.Interaction):
        server_id = ctx.guild.id
        name = self.name.value
        category = self.category.value
        unit = self.unit.value
        quantity = self.quantity.value
        threshold = self.threshold.value
        # 確定quantity, threshold是整數
        try:
            if quantity: quantity = int(quantity)
            if threshold: threshold = int(threshold)
        except:
            self.embed.description = '❌please input integer for quantity and threshold'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確定名字不重複
        if name in select_inventory_item_by_column(server_id=server_id, column='name'):
            self.embed.description = '❌name already exist'
            await ctx.response.edit_message(embed=self.embed)
            return
        
        # 增加該品項
        add_inventory_item_table(
                server_id=server_id,
                name=name, 
                category=category,
                unit=unit,
                quantity=quantity,
                threshold=threshold
                )
        
        # 告知使用者他成功了
        self.embed.description = f'添加成功！！！\nname: {name}\ncategory: {category}\nunit: {unit}\nquantity: {quantity}\nthreshold: {threshold}'
        file = show_table(data = select_inventory_item_all(server_id=server_id, ItemOrLog='items'), ctx=ctx, ItemOrLog='items', text='所有品項')
        self.embed.set_image(url='attachment://inventory.png')
        await ctx.response.edit_message(embed=self.embed, attachments=[file])
        
        # 更新google sheet
        item_url, _ = select_server_sheet_url(server_id=server_id)
        sheet_update_item(ctx, url=item_url)
# Modal 刪除品項
class deleteItemModal(discord.ui.Modal, title = '刪除品項'):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout = 180)
        self.embed = embed
        self.name= TextInput(label='名稱', placeholder='Mia is poo', max_length=30, min_length=1, required=False)
        self.item_id = TextInput(label='item_id', placeholder='ex: 1, 4, 5', max_length=11, required=False)
        self.add_item(self.name)
        self.add_item(self.item_id)
    
    async def on_submit(self, ctx: discord.Interaction):
        server_id = ctx.guild.id
        name = self.name.value
        item_id = self.item_id.value
        # 確認有值
        if not name and not item_id:
            self.embed.description = '❌你啥都不說難道以為甲魚通靈的出來嗎87 \n甲魚就是個87他通靈不出來'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認ID是數字
        try:
            if item_id != '': item_id = int(item_id)
        except:
            self.embed.description = '❌id要數字阿87'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認名字存在
        if name and name not in select_inventory_item_by_column(server_id=ctx.guild.id, column='name'):
            self.embed.description = f'❌{name} not in inventory'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認 ID 存在
        if item_id != '' and int(item_id) not in select_inventory_item_by_column(server_id=ctx.guild.id, column='item_id'):
            await ctx.response.edit_message('id不存在 白癡')
            return
        okma = 0
        if item_id != '' and name:
            data = select_inventory_item_all(ctx.guild.id, ItemOrLog='items')
            for line in data:
                if  int(item_id) == line[0] and name == line[1]: 
                    okma = 1
                    break
            if not okma:
                self.embed.description = f'❌{item_id}, {name} different lah idiot'
                await ctx.response.edit_message(embed=self.embed)
                return
        # 刪除該品項
        delete_inventory_item_table(server_id=ctx.guild.id, name=name, item_id=item_id)
        # 告知使用者他成功了
        self.embed.description = f'刪除成功！！！\nitem_id: {item_id}\nname: {name}\n'
        file = show_table(data = select_inventory_item_all(server_id=server_id, ItemOrLog='items'), ctx=ctx, ItemOrLog='items', text='所有品項')
        self.embed.set_image(url='attachment://inventory.png')
        await ctx.response.edit_message(embed=self.embed, attachments=[file])
        
        # 更新google sheet
        item_url, log_url = select_server_sheet_url(server_id=ctx.guild.id)
        sheet_update_item(ctx, url=item_url)
        sheet_update_log(ctx, url=log_url)
# Modal 更新倉庫
class updateItemModal(discord.ui.Modal, title = '更新倉庫'):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout = 180)
        self.embed = embed
        self.name= TextInput(label='名稱', placeholder='Mia is poo', max_length=30, min_length=1, required=False)
        self.item_id = TextInput(label='item_id', placeholder='ex: 1, 4, 5', max_length=11, required=False)
        self.change_amount = TextInput(label='改變數量', placeholder='ex: 1, -4, 5', max_length=11)
        self.note = TextInput(label='備註', placeholder='ex: 是AB太87半夜偷偷吃掉的', max_length=50, required=False)
        self.add_item(self.name)
        self.add_item(self.item_id)
        self.add_item(self.change_amount)
        self.add_item(self.note)
    async def on_submit(self, ctx: discord.Interaction):
        server_id = ctx.guild.id
        name = self.name.value
        item_id = self.item_id.value
        change_amount = self.change_amount.value
        note = self.note.value
        # 確認有值
        if not name and not item_id:
            self.embed.description = '❌你啥都不說難道以為甲魚通靈的出來嗎87 \n甲魚就是個87他通靈不出來'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認ID是數字
        try:
            if item_id != '': item_id = int(item_id)
        except:
            self.embed.description = '❌id要數字阿87'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認名字存在
        if name and name not in select_inventory_item_by_column(server_id=ctx.guild.id, column='name'):
            self.embed.description = f'❌{name} not in inventory'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認 ID 存在
        if item_id != '' and int(item_id) not in select_inventory_item_by_column(server_id=ctx.guild.id, column='item_id'):
            self.embed.description = '❌id不存在 白癡'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認name, item_id 有對應到
        okma = 0
        if item_id != '' and name:
            data = select_inventory_item_all(ctx.guild.id, ItemOrLog='items')
            for line in data:
                if  int(item_id) == line[0] and name == line[1]: 
                    okma = 1
                    break
            if not okma:
                self.embed.description = f'❌{item_id}, {name} different lah idiot'
                await ctx.response.edit_message(embed=self.embed)
                return
        # 將 item_id 找出來
        if item_id == '':
            data = select_inventory_item_all(ctx.guild.id, ItemOrLog='items')
            for i in data:
                if i[1] == name: item_id = int(i[0])
        # 確認change amount 是數字
        try:
            change_amount = int(str(change_amount))
        except:
            self.embed.description = '❌change amount要數字阿87'
            await ctx.response.edit_message(embed=self.embed)
            return        
        # 更新倉庫及添加紀錄
        update_inventory_item_table(server_id=ctx.guild.id, item_id=item_id, change_amount=change_amount, note=note)
        
        # 告知使用者他成功了
        self.embed.description = f'更新成功！！！\nitem_id: {item_id}\nname: {name}\nchange_amount: {change_amount}\nnote: {note}'
        file = show_table(data = select_inventory_item_all(server_id=server_id, ItemOrLog='items'), ctx=ctx, ItemOrLog='items', text='所有品項')
        self.embed.set_image(url='attachment://inventory.png')
        await ctx.response.edit_message(embed=self.embed, attachments=[file])
        
        # 更新google sheet
        item_url, log_url = select_server_sheet_url(server_id=ctx.guild.id)
        sheet_update_item(ctx, url=item_url)
        sheet_update_log(ctx, url=log_url)
# Modal 搜尋品項
class searchItemModal(discord.ui.Modal, title = '搜尋品項'):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout = 180)
        self.embed = embed
        self.name= TextInput(label='名稱', placeholder='Mia is poo', max_length=30, min_length=1, required=False)
        self.category = TextInput(label='種類', placeholder='ex: 肉類, 蔬菜', max_length=30, required=False)
        self.unit = TextInput(label='單位', placeholder='ex: 個, 公斤', max_length=20, min_length=1, required=False)
        self.add_item(self.name)
        self.add_item(self.category)
        self.add_item(self.unit)
    
    async def on_submit(self, ctx: discord.Interaction):
        name = self.name.value
        category = self.category.value
        unit = self.unit.value
        # 確認有值
        if not name and not category and not unit:
            self.embed.description = '❌你啥都不說難道以為甲魚通靈的出來嗎87 \n甲魚就是個87他通靈不出來'
            await ctx.response.edit_message(embed=self.embed)
            return
        data = search_inventory_item(server_id=ctx.guild.id, name=name, category=category, unit=unit)
        file = show_table(data = data, ctx=ctx, ItemOrLog='items', text='搜尋結果')
        await ctx.response.edit_message(attachments=[file])
# Modal 更新sheet url
class updateSheetUrlModal(discord.ui.Modal, title = '更新sheet url (如欲放在同一檔案則重複貼上即可)'):
    def __init__(self, embed: discord.Embed):
        super().__init__(timeout = 180)
        self.embed = embed
        self.item_url= TextInput(label='倉庫sheet url', placeholder='ur url', required=False)
        self.log_url = TextInput(label='倉庫紀錄sheet url', placeholder='ur url', required=False)
        self.add_item(self.item_url)
        self.add_item(self.log_url)
    
    async def on_submit(self, ctx: discord.Interaction):
        item_url = self.item_url.value
        log_url = self.log_url.value
        # 確認 url 有效
        if item_url and not validators.url(item_url):
            self.embed.description = '❌item url不正確'
            await ctx.response.edit_message(embed=self.embed)
            return
        if log_url and not validators.url(log_url):
            self.embed.description = '❌log url不正確'
            await ctx.response.edit_message(embed=self.embed)
            return
        # 確認 url 是google sheet
        varify = 'docs.google.com/spreadsheets'
        if item_url and varify not in item_url:
            self.embed.description = '❌item url不是google sheet'
            await ctx.response.edit_message(embed=self.embed)
            return
        if log_url and varify not in log_url:
            self.embed.description = '❌log url不是google sheet'
            await ctx.response.edit_message(embed=self.embed)
            return
        
        self.embed.description =  f'✅更新成功\nitem url: {item_url}\nlog url: {log_url}'
        await ctx.response.edit_message(embed=self.embed)
        
        update_server_sheet_url(server_id=ctx.guild.id, item_url=item_url, log_url=log_url)
        
           
     
     
        
class MyButton(discord.ui.Button):
    def __init__(self, url: str, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.primary, url=url)
        print(get_timestamp(), 'url', url)


# View 改變倉庫
class inventoryListView(discord.ui.View):
    def __init__(self, ctx: discord.Interaction):
        super().__init__(timeout=600) 
        self.ctx = ctx
        self.server_id = self.ctx.guild.id
        self.embed = discord.Embed(
            title= f"[倉庫] {ctx.guild.name}",
            description='a;lsjdkfl;akjsf',
            color=0x4ebcbe
        )
        # Test
        item_url, log_url = select_server_sheet_url(server_id=self.server_id)
        default_item_url = global_original_item_url
        default_log_url = global_original_log_url

        if item_url: self.add_item(MyButton(url=item_url, label='倉庫sheet'))
        if log_url: self.add_item(MyButton(url=log_url, label='倉庫紀錄sheet'))

    # Button 增加品項   
    @discord.ui.button(
        label = "增加品項", 
        style = discord.ButtonStyle.gray
    )
    async def add_column(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(addItemModal(embed=self.embed))

    # Button 刪除品項
    @discord.ui.button(
        label = "刪除品項", 
        style = discord.ButtonStyle.gray
    )
    async def delete_column(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(deleteItemModal(embed=self.embed))

    # Button 更新倉庫數量
    @discord.ui.button(
        label = "更新倉庫數量", 
        style = discord.ButtonStyle.gray
    )
    async def update_quantity(self, ctx:discord.Interaction, button:discord.ui.button):
        await ctx.response.send_modal(updateItemModal(embed=self.embed))
    
    # Button 搜尋品項
    @discord.ui.button(
        label = "搜尋品項", 
        style = discord.ButtonStyle.gray
    )
    async def search_item(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(searchItemModal(embed=self.embed))
    
    # Button 顯示倉庫表格
    @discord.ui.button(
        label = "所有品項", 
        style = discord.ButtonStyle.gray
    )
    async def show_all(self, ctx: discord.Interaction, button: discord.ui.Button):
        file = show_table(data = select_inventory_item_all(server_id=self.server_id, ItemOrLog='items'), ctx=self.ctx, ItemOrLog='items', text='所有品項')
        self.embed.set_image(url='attachment://inventory.png')
        await ctx.response.edit_message(embed=self.embed, attachments=[file])

    # Button 顯示倉庫紀錄
    @discord.ui.button(
        label = "顯示紀錄", 
        style = discord.ButtonStyle.gray
    )
    async def show_all_logs(self, ctx: discord.Interaction, button: discord.ui.Button):
        file = show_table(data = select_inventory_item_all(server_id=self.server_id, ItemOrLog='logs'), ctx=self.ctx, ItemOrLog='logs', text='所有紀錄')
        self.embed.set_image(url='attachment://inventory.png')
        await ctx.response.edit_message(embed=self.embed, attachments=[file])

    # Button 顯示低於安全數量的品項
    @discord.ui.button(
        label = "低於安全數量", 
        style = discord.ButtonStyle.gray
    )
    async def show_item_safety(self, ctx: discord.Interaction, button: discord.ui.Button):
        file = show_table(data = select_inventory_item_safety(ctx.guild.id), ctx=self.ctx, ItemOrLog='items', text='低於安全數量的品項')
        self.embed.set_image(url='attachment://inventory.png')
        await ctx.response.edit_message(embed=self.embed, attachments=[file])

    # Button sheet指引
    @discord.ui.button(
        label = "sheet指引", 
        style = discord.ButtonStyle.gray
    )
    async def show_sheet_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 檔案與預設資料
        guide_image_path = global_sheet_guide_path
        file = discord.File(guide_image_path, filename='sheetGuide.jpg')

        default_author_email = 'python-sheet-api@python-sheet-basic.iam.gserviceaccount.com'
        default_item_url = global_original_item_url
        default_log_url = global_original_log_url

        # 根據伺服器 ID 取得對應的 sheet URL
        item_url, log_url = select_server_sheet_url(server_id=self.server_id)
        item_url = None if item_url == default_item_url else item_url
        log_url = None if log_url == default_log_url else log_url

        # 組合訊息內容
        guide_text = f'''**❤️💩🥕👙❤️‍🔥SHEET 指引❤️‍🔥👙🥕💩❤️**
        
1. 🔓 打開你想使用的 Google Sheet。

2. 🧑‍🤝‍🧑 點擊右上角的「分享」按鈕。

3. 📨 在「新增協作者」的欄位中輸入以下信箱：
```fix\n{default_author_email}\n```
4. ✅ 確認權限設為「編輯者」，然後按下「完成」。

5. 📝 回到 Discord，按下按鈕「更新sheet url」後提交你的 Sheet 連結！
👉 沒有提交的話，系統無法幫你連接資料喔！

📌 小提醒：
這個步驟只需要設定一次～設定好後，就可以愉快使用倉庫功能啦 🎉💼

有問題隨時 tag 我們！我們會飛奔過來幫你 🚀❤️\n\n\n
'''
        
        if item_url:
            guide_text += f"📦 [倉庫資料表（item sheet）]({item_url})\n"
        else:
            guide_text += "📦 尚未設定倉庫資料表 URL\n"

        if log_url:
            guide_text += f"📝 [紀錄資料表（log sheet）]({log_url})\n"
        else:
            guide_text += "📝 尚未設定紀錄資料表 URL\n"
       
        # 更新 embed 顯示
        self.embed.description = guide_text
        self.embed.set_image(url='attachment://sheetGuide.jpg')

        await interaction.response.edit_message(embed=self.embed, attachments=[file])
        
    # Button 更新sheet url
    @discord.ui.button(
        label = "更新sheet url", 
        style = discord.ButtonStyle.gray
    )
    async def update_sheet_url(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.send_modal(updateSheetUrlModal(embed=self.embed))
    
    # Button 取消
    @discord.ui.button(
        label = "取消", 
        style = discord.ButtonStyle.gray
    )
    async def cancel(self, ctx: discord.Interaction, button: discord.ui.Button):
        await self.ctx.delete_original_response()
        print(f'[{get_timestamp()}]', 'inventoryListView cancel')
        await self.stop()
    
    
    async def on_timeout(self):
        await self.ctx.delete_original_response()
        print(f'[{get_timestamp()}]', 'inventoryListView timeout')

#主程式
class Inventrory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # 改變倉庫
    @app_commands.command(name = 'food', description='dfsgjkahkjglhkdjbn')
    async def food(self, ctx:discord.Interaction):
        server_id = ctx.guild.id
        
        # 創建倉庫 if not exist
        if not is_table_exist(server_id):
            create_new_tables(server_id)
        # 紀錄伺服器 if not exist
        if not is_server_exist(server_id):
            add_server(server_id, ctx.guild.name)
        
        embed = discord.Embed(
            title= f"[倉庫] {ctx.guild.name}",
            description='a;lsjdkfl;akjsf',
            color=0x4ebcbe
        )
        file = show_table(data = select_inventory_item_all(server_id=server_id, ItemOrLog='items'), ctx=ctx, ItemOrLog='items', text='所有品項')    
        embed.set_image(url='attachment://inventory.png')
        await ctx.response.send_message(embed=embed, files=[file], view=inventoryListView(ctx))
        
       
        # 初始化 google sheet
        item_url, log_url = select_server_sheet_url(server_id=server_id)
        sheet_update_item(ctx, url=item_url)
        sheet_update_log(ctx, url=log_url)
        
        
     
    
        
    

async def setup(bot):
    await bot.add_cog(Inventrory(bot))
