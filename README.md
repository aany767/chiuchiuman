# 咪咪寶寶部署說明

需要的 Python 套件皆列於 `requirements.txt`。

## 檔案內容 (若不會使用可將其刪除)

- 基本功能
    - `cogs/basics.py`
- 提醒功能
    - `cogs/remind.py`
    - `cogs/send.py`
    - `JSON/remind.json`
    - `JSON/template.json`
- 點餐、查看訂單功能
    - `cogs/setrole.py`
    - `cogs/menuedit.py`
    - `cogs/order.py`
    - `JSON/r_admin_role.json`
    - `JSON/menu.json`
    - `JSON/cart.json`
    - `JSON/index.html`
    - `JSON/style.css`
- 倉庫
    - `cogs/inventory.py`

## 需修改的地方(功能部份需要使用再修改即可)

- 主程式
    1. `main.py` line 12
- 功能
    - 點餐
        1. `cogs/set_role.py` line 12
        2. `cogs/manage.py` line 12, 13, 23
        3. `cogs/menuedit.py` line 12-14
        4. `cogs/order.py` line 12-14
        5. `cogs/index.html` line 29
    - 提醒
        1. `cogs/remind.py` line 12-13
        2. `cogs/send.py` line 16
    - 倉庫
        1. `cogs/inventory.py` line 11-15, 110-114

## 用網站頁面查看訂單

先架設 n8n，詳細教學在[這裡](https://docs.n8n.io/hosting/)

建立一個新的 workflow，匯入 `n8n_workflow/finish_order_workflow.json` ，即出現兩個節點：

![image](https://github.com/user-attachments/assets/217cc602-69b1-4743-a280-f8b5a196da14)

點入右側SSH節點，設定必要內容 (橘色標記處)：

![image](https://github.com/user-attachments/assets/b0a711f9-a926-4039-a20f-aa0e83aa7f53)

上方為建立連接至運行伺服器的憑證，下方則更改為 `n8n_workflow/del_order.py` 的路徑。

建立完成後，記得於 `JSON/index.html` 更改 webhook URL，開始測試工作流，成功後便可將 webhook 類型切換至 Production URL。

建立或進入一個 screen session，進入 `cogs` 目錄，執行：

```
python -m http.server [port_number]
```

即可在 `http://localhost:[port_number]` 查看網站！(也可使用其他方式部署網站)
