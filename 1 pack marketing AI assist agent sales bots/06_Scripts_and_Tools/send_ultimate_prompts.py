import re
import requests

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

with open("smm_brand_ai/ai_content/love_stories/storyboard/veo31_vertex_generation_pack.md", "r", encoding="utf-8") as f:
    text_vis = f.read()

with open("smm_brand_ai/ai_content/love_stories/storyboard/veo31_voiceover_8s_timing.md", "r", encoding="utf-8") as f:
    text_voice = f.read()

pattern_vis = re.compile(r'## VEO-(\d{2}).*?```text\n(.*?)\n```', re.DOTALL)
matches_vis = dict(pattern_vis.findall(text_vis))

pattern_voice = re.compile(r'## VEO-(\d{2}).*?```text\n(.*?)\n```', re.DOTALL)
matches_voice = dict(pattern_voice.findall(text_voice))

global_prefix = "Vertical 9:16 realistic cinematic romantic short film in a cozy modern coffee shop in Almaty. Use the provided character reference images and preserve the same heroes, outfits, hair, body proportions, cafe location and warm cinematic style. The woman is the same young Kazakh woman in a beige knit sweater drawing in a sketchbook. The man is the same young Kazakh man in a black hoodie near the coffee bar. Smooth stabilized camera, natural emotional acting, warm cafe lighting, shallow depth of field, soft bokeh. No text overlays, no readable text, no subtitles, no logos, no watermark. "
voice_style = "Russian female voiceover, warm intimate storytelling tone, calm pace, soft emotional delivery, no subtitles, no on-screen text."

msgs = []
curr_msg = "🎛 <b>ПОЛНЫЙ ПАК С НАСТРОЙКАМИ И ОЗВУЧКОЙ</b> (Часть 1)\n\n"
part = 1

for num in sorted(matches_vis.keys()):
    visual_prompt = global_prefix + matches_vis[num].strip()
    voiceover_text = matches_voice.get(num, "Нет озвучки").strip()
    
    chunk = f"🎬 <b>СЦЕНА VEO-{num}</b>\n"
    chunk += f"<b>Настройки:</b> Aspect Ratio: 9:16 | Duration: 8s\n"
    chunk += f"<b>Images:</b> start frame -> <code>veo31_{num}_start.png</code>\n\n"
    
    chunk += f"🖼 <b>Visual Prompt:</b>\n<code>{visual_prompt}</code>\n\n"
    
    chunk += f"🎙 <b>Audio / Voiceover:</b>\n<code>{voice_style}\n\n{voiceover_text}</code>\n"
    chunk += "— — — — — —\n\n"
    
    if len(curr_msg) + len(chunk) > 4000:
        msgs.append(curr_msg)
        part += 1
        curr_msg = f"🎛 <b>ПОЛНЫЙ ПАК С НАСТРОЙКАМИ И ОЗВУЧКОЙ</b> (Часть {part})\n\n"
        curr_msg += chunk
    else:
        curr_msg += chunk

msgs.append(curr_msg)

for m in msgs:
    res = requests.post(API_URL, json={'chat_id': CHAT_ID, 'text': m, 'parse_mode': 'HTML'})
    print(res.json())
