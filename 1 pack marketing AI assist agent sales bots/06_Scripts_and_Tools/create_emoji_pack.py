import os, requests, time, socket
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

socket.setdefaulttimeout(30)
load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
USER_ID = 888005446
REG_PACK = "nns_r_1781337023_by_test14fbot"
NEW_EMOJI_PACK_NAME = f"nns_e_{int(time.time())}_by_test14fbot"
NEW_EMOJI_PACK_TITLE = "AI Agents | @nnsvt"

def crop_for_emoji(img):
    # img is 512x512 RGBA
    # Вырезаем центральный квадрат 360x360 с небольшим смещением вверх
    # Это отрежет нижний мелкий текст и сфокусирует кадр на лице/иконке
    box = (76, 20, 436, 380)
    cropped = img.crop(box)
    
    # Custom emojis MUST be exactly 100x100
    resized = cropped.resize((100, 100), Image.Resampling.LANCZOS)
    return resized

def main():
    print("Fetching original stickers...")
    pack_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={REG_PACK}").json()
    if not pack_resp.get('ok'):
        print("Error fetching pack:", pack_resp)
        return
        
    stickers = pack_resp['result']['stickers']
    emoji_files = []
    
    for i, st in enumerate(stickers):
        emoji_char = st['emoji']
        file_id = st['file_id']
        f_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
        if f_resp.get('ok'):
            file_path = f_resp['result']['file_path']
            img_data = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}").content
            img = Image.open(BytesIO(img_data)).convert("RGBA")
            
            emoji_img = crop_for_emoji(img)
            
            buf = BytesIO()
            emoji_img.save(buf, format="WEBP")
            buf.seek(0)
            
            emoji_files.append({
                'buffer': buf,
                'emoji': emoji_char
            })
            print(f"Processed {i+1}/{len(stickers)}")

    print("Creating new custom emoji set...")
    first = emoji_files[0]
    upload_resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile",
        data={'user_id': USER_ID, 'sticker_format': 'static'},
        files={'sticker': ('0.webp', first['buffer'].getvalue(), 'image/webp')}
    ).json()
    
    if not upload_resp.get('ok'):
        print("Upload failed:", upload_resp)
        return
        
    first_file_id = upload_resp['result']['file_id']
    
    create_payload = {
        'title': "AI Agents MVP | @nnsvt",
        'name': f"nns_crop_{int(time.time())}_by_test14fbot",
        'stickers': [
            {
                'sticker': f"attach://{first_file_id}",
                'emoji': "🚀"
            }
        ],
        'sticker_format': 'static',
        'sticker_type': 'regular',  # Changed to regular
        'needs_repainting': False
    }
    
    create_resp = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/createNewStickerSet", data=create_payload).json()
    print("Create Set:", create_resp)
    
    if not create_resp.get('ok'):
        return

    for i in range(1, len(emoji_files)):
        item = emoji_files[i]
        upl = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile",
            data={'user_id': USER_ID, 'sticker_format': 'static'},
            files={'sticker': (f'{i}.webp', item['buffer'].getvalue(), 'image/webp')}
        ).json()
        
        if upl.get('ok'):
            fid = upl['result']['file_id']
            add_resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/addStickerToSet",
                data={
                    'user_id': USER_ID,
                    'name': NEW_EMOJI_PACK_NAME,
                    'sticker': '{"sticker":"' + fid + '", "format":"static", "emoji_list":["' + item['emoji'] + '"]}'
                }
            ).json()
            print(f"Added {i+1}:", add_resp.get('ok'))
            
    link = f"https://t.me/addstickers/{NEW_EMOJI_PACK_NAME}"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
        'chat_id': USER_ID, 
        'text': f"🔥 **Твой АДАПТИРОВАННЫЙ Эмодзи-пак готов!**\n\nЯ обрезал все лишнее и оставил только крупные лица/иконки (100x100). Теперь в тексте они будут смотреться идеально четко, а при клике на них вылезет жирная плашка: **AI Agents | @nnsvt**.\n\nЗабирай: {link}",
        'parse_mode': 'Markdown'
    })

if __name__ == "__main__":
    main()
