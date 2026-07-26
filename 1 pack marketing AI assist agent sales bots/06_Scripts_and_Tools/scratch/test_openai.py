import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("AIHUBMIX_API_KEY")
print(f"Testing key on AIHubMix: {key[:15]}...{key[-5:] if key else ''}")

# Используем базовый URL AIHubMix
client = OpenAI(api_key=key, base_url="https://api.aihubmix.com/v1")

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Привет, это тест. Ответь одним словом 'ОК'."}],
        timeout=10
    )
    print("Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
