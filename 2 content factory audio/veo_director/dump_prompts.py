import sys
import os
sys.path.append('.')
from veo_director_skill import parse_scenario_to_scenes, load_environment
from google import genai

def dump():
    with open('assets/scenarios/test_scenario.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    client = genai.Client(api_key=load_environment())
    scenes = parse_scenario_to_scenes(client, text)

    out_path = 'assets/scenarios/prompts_list.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# Сгенерированные промпты для сцен\n\n')
        for s in scenes:
            f.write(f"### Сцена {s['scene_number']}\n")
            f.write(f"**Голос:** *{s['voice_text']}*\n")
            f.write(f"**Промпт Veo (Англ):** `{s['visual_prompt']}`\n\n")
    print(f"Промпты сохранены в {out_path}")

if __name__ == '__main__':
    dump()
