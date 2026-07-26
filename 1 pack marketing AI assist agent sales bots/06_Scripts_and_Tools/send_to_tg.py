import os
import requests
import time

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

def send_file(filepath, caption):
    with open(filepath, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': CHAT_ID, 'caption': caption}
        resp = requests.post(API_URL, data=data, files=files)
        print(f"Sent {filepath}: {resp.status_code} {resp.text}")
        time.sleep(1)

# Send AGENTS.md (Rules)
send_file(".agents/AGENTS.md", "Глобальные правила (Rules)")

# Combine skills into one file to avoid spamming 71 files
with open("all_skills.md", "w") as out:
    out.write("# Все Скиллы (Skills)\n\n")
    skills_dir = ".agents/skills"
    if os.path.exists(skills_dir):
        for skill in sorted(os.listdir(skills_dir)):
            skill_md = os.path.join(skills_dir, skill, "SKILL.md")
            if os.path.exists(skill_md):
                out.write(f"\n\n## Скилл: {skill}\n")
                with open(skill_md, "r") as f:
                    out.write(f.read())
                    
send_file("all_skills.md", "Все скиллы из Cline Stack (объединенный файл)")
