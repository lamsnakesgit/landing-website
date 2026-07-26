import os
import requests
import time

base_dir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"

generated_files = [os.path.join(base_dir, f"carousel_slide_{i}.png") for i in range(1, 7)]

print("Checking files...")
for file_path in generated_files:
    if os.path.exists(file_path):
        print(f"Found: {file_path}")
    else:
        print(f"Waiting for: {file_path} - please run this when generation finishes.")

print("Sending to Telegram...")
BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

for file_path in generated_files:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as photo:
                requests.post(API_URL, data={'chat_id': CHAT_ID}, files={'photo': photo})
                print(f"Sent: {file_path}")
                time.sleep(1) # sleep to avoid rate limits
        except Exception as e:
            print(f"Send error: {e}")

print("Done!")
