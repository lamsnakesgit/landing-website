import requests

BOT_TOKEN = "8775727439:AAG2Iql9PzF9cSizzdRk8UWp9llZn5HC0XM"
CHAT_ID = "888005446"
PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"
FILE_PATH = "sticker_tongue.png"

print("Uploading sticker file...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile"
with open(FILE_PATH, "rb") as f:
    resp = requests.post(url, data={'user_id': CHAT_ID, 'sticker_format': 'static'}, files={'sticker': f})

res = resp.json()
print("Upload response:", res)

if res.get('ok'):
    file_id = res['result']['file_id']
    print(f"File ID obtained: {file_id}")
    
    add_url = f"https://api.telegram.org/bot{BOT_TOKEN}/addStickerToSet"
    payload = {
        'user_id': CHAT_ID,
        'name': PACK_NAME,
        'sticker': {
            "sticker": file_id,
            "emoji_list": ["👅", "💰"]
        }
    }
    
    print("Adding sticker to set...")
    resp_add = requests.post(add_url, json=payload)
    print("Add response:", resp_add.json())
else:
    print("Failed to upload.")
