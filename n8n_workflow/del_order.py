# 此檔案請修改第 5 行 #

import json, sys

cart_file = "CART_FILE_PATH"  # Replace with the actual path to your cart file

guild_id = sys.argv[1]
table_num = sys.argv[2]

with open(cart_file, 'r') as f:
    data = json.load(f)

del data[guild_id][table_num]
with open(cart_file, 'w') as f:
    json.dump(data, f, indent=4)
