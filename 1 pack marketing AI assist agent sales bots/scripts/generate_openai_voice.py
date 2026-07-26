import os
import sys
import requests
import argparse

def get_api_key():
    """Считывает OPENAI_API_KEY из файла .env в корне проекта."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        # Если запускаем из корня
        env_path = ".env"
        
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=")[1].strip()
                    
    # Проверяем переменную окружения системы
    return os.environ.get("OPENAI_API_KEY")

def generate_voice(text, voice_name, output_path, api_key):
    """Отправляет запрос в OpenAI TTS API для генерации озвучки."""
    if not api_key:
        print("Ошибка: API-ключ OpenAI не найден. Убедитесь, что OPENAI_API_KEY прописан в файле .env.")
        return False
        
    print(f"Отправка запроса на озвучку текста (голос: {voice_name})...")
    
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Поддерживаемые голоса: alloy, echo, fable, onyx, nova, shimmer
    # tts-1 подходит для быстрого рендеринга в реальном времени
    payload = {
        "model": "tts-1",
        "input": text,
        "voice": voice_name,
        "response_format": "mp3"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Озвучка успешно создана и сохранена в: {output_path}")
            return True
        else:
            print(f"Ошибка API OpenAI (Код {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"Сбой при отправке запроса: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Автоматическая генерация озвучки через OpenAI TTS.")
    parser.add_argument("--text", required=True, help="Текст для озвучки на русском языке.")
    parser.add_argument(
        "--voice", 
        default="onyx", 
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        help="Голос для озвучки (onyx - низкий мужской, echo - средний мужской, nova - женский)."
    )
    parser.add_argument("--output", required=True, help="Путь для сохранения готового файла .mp3.")
    
    args = parser.parse_args()
    
    api_key = get_api_key()
    generate_voice(args.text, args.voice, args.output, api_key)

if __name__ == "__main__":
    main()
