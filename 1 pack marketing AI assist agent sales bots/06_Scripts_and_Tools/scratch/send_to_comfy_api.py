import json
import urllib.request
import urllib.parse
import uuid
import sys
import os

# Адрес туннеля
COMFY_SERVER = "https://vanilla-sign-covering-difficulty.trycloudflare.com"
CLIENT_ID = str(uuid.uuid4())

def upload_dummy_image(server_url):
    print("📦 Подготовка тестового изображения для загрузки на сервер ComfyUI...")
    
    # Создадим временную картинку размером 1x1 пиксель, если её нет локально
    image_filename = "reference_face.png"
    if not os.path.exists(image_filename):
        # Самый простой PNG 1x1 в бинарном формате
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(image_filename, "wb") as f:
            f.write(png_data)
            
    # Загружаем файл через multipart/form-data POST на /upload/image
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    url = f"{server_url}/upload/image"
    
    with open(image_filename, "rb") as f:
        file_content = f.read()
        
    # Формируем тело multipart запроса вручную, чтобы не тащить сторонние библиотеки
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{image_filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode('utf-8') + file_content + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="type"\r\n\r\ninput\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
        f"--{boundary}--\r\n"
    ).encode('utf-8')
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body))
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print(f"✅ Изображение '{res.get('name')}' успешно загружено на сервер!")
            return res.get('name')
    except Exception as e:
        print(f"❌ Не удалось загрузить референс: {e}")
        return None

def send_prompt(server_url, workflow, client_id):
    # Перед отправкой воркфлоу загрузим изображение, чтобы не было ошибки 400 Bad Request на ноде LoadImage
    uploaded_name = upload_dummy_image(server_url)
    if not uploaded_name:
        uploaded_name = "reference_face.png" # Запасное имя
        
    # Обновляем имя картинки в ноде LoadImage (ID "12")
    workflow["12"]["inputs"]["image"] = uploaded_name
    
    url = f"{server_url}/prompt"
    payload = {
        "prompt": workflow,
        "client_id": client_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("🚀 Успешно отправлено в очередь генерации!")
            print(f"ID Задачи (Prompt ID): {res_data.get('prompt_id')}")
            return res_data
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка сервера {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Ошибка отправки запроса: {e}")
        return None

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else COMFY_SERVER
    # Убираем слеш в конце если есть
    if url_arg.endswith("/"):
        url_arg = url_arg[:-1]
        
    # Загружаем JSON воркфлоу
    with open("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/cv_hunt_career/workflow_face_transfer.json", "r") as f:
        workflow_data = json.load(f)
        
    send_prompt(url_arg, workflow_data, CLIENT_ID)
