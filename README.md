## 需修改的地方(功能部份需要使用再修改即可)

- 主程式  
    1. ```main.py``` line 12  
- 功能
    - 點餐
        1. `cogs/set_role.py` line 12
        4. `cogs/manage.py` line 12, 13, 23  
        5. `cogs/menuedit.py` line 12-14  
        6. `cogs/order.py` line 12-14
        1. `cogs/index.html` line 29 
    - 提醒
        1. ```cogs/remind.py``` line 12-13
        2. ```cogs/send.py``` line 16

## 用網站頁面查看訂單
先架設 n8n，詳細教學在[這裡](https://docs.n8n.io/hosting/)    

建立一個 screen session
<pre>screen -R [any name]</pre> 
進入 `cogs` 目錄，執行
<pre>python -m http.server [port]</pre>
即可在 `http://localhost:1234` 查看網站！
