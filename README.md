## 檔案內容 (若不會使用可將其刪除)
- 基本功能
    - `cogs/basics.py`
- 提醒功能
    - `cogs/remind.py`
    - `cogs/send.py`
    - `remind.json`
    - `template.json`
- 點餐、查看訂單功能
    - `cogs/setrole.py`
    - `cogs/menuedit.py`
    - `cogs/order.py`
    - `r_admin_role.json`
    - `menu.json`
    - `cart.json`
    - `index.html`
    - `style.css`


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

建立一個新的 workflow，匯入 `n8n_workflow/finish_order_workflow.json` ，即出現兩個節點：
![image](https://github.com/user-attachments/assets/f9081468-cd3b-4b51-b352-efb3974bc037)



建立一個 screen session
```
screen -R [any name]
```
進入 `cogs` 目錄，執行
```
python -m http.server [port]
```
即可在 `http://localhost:1234` 查看網站！
