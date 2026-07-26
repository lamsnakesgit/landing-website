import os
import time
# Для установки библиотеки выполните в терминале: pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark

def generate_seedance_video(api_key, model_endpoint_id, prompt):
    """
    Генерация видео с помощью модели Seedance через BytePlus/Volcengine (ModelArk).
    """
    # Инициализация клиента с переданным API-ключом
    # Если используете глобальный BytePlus: base_url="https://ark.ap-southeast.bytepluses.com/api/v3"
    # Если китайский Volcengine: base_url="https://ark.cn-beijing.volces.com/api/v3"
    
    client = Ark(
        base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
        api_key=api_key,
    )

    print(f"[*] Отправка промпта на генерацию: '{prompt}'...")
    
    try:
        # Шаг 1: Создание задачи на генерацию
        create_result = client.content_generation.tasks.create(
            model=model_endpoint_id,
            content=[
                {
                    "type": "text", 
                    "text": prompt
                }
            ]
        )
        
        task_id = create_result.id
        print(f"[+] Задача успешно создана! ID: {task_id}")
        
    except Exception as e:
        print(f"[-] Ошибка при создании задачи (проверьте API ключ или лимиты): {e}")
        return

    # Шаг 2: Ожидание готовности видео (Polling)
    print("[*] Ждем завершения генерации (это может занять несколько минут)...")
    
    while True:
        try:
            get_result = client.content_generation.tasks.get(task_id=task_id)
            status = get_result.status
            
            if status == "succeeded":
                print("\n[🎉] Видео готово!")
                print("Ответ API:", get_result)
                break
            elif status == "failed":
                print("\n[-] Ошибка генерации (возможно, сработал фильтр контента).")
                print("Детали:", get_result)
                break
            else:
                print(f"[{status}] В процессе... ждем 10 секунд.")
                time.sleep(10)
                
        except Exception as e:
            print(f"[-] Ошибка при проверке статуса: {e}")
            break

if __name__ == "__main__":
    # --- НАСТРОЙКИ ---
    
    # Сюда вы вставляете свежий API-ключ от нового аккаунта (когда старый сгорает, просто меняете эту строку)
    CURRENT_API_KEY = "ВАШ_СВЕЖИЙ_API_KEY"
    
    # ID вашего Endpoint (создается в панели ModelArk / Volcengine после выбора модели Seedance)
    # Например: ep-202412345678-abcd
    MODEL_ENDPOINT_ID = "ВАШ_ENDPOINT_ID"
    
    # Описание желаемого видео
    PROMPT = "Cinematic shot of a cybernetic cat walking in neon city, highly detailed, 4k resolution --resolution 720p --duration 5"
    
    # Запуск
    if CURRENT_API_KEY == "ВАШ_СВЕЖИЙ_API_KEY":
        print("Пожалуйста, укажите ваш API_KEY и MODEL_ENDPOINT_ID в коде!")
    else:
        generate_seedance_video(CURRENT_API_KEY, MODEL_ENDPOINT_ID, PROMPT)
