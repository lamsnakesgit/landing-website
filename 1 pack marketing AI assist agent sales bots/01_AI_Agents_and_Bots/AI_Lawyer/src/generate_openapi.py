import json
from app import app

def generate_spec():
    # Получаем сгенерированную схему OpenAPI от FastAPI
    openapi_schema = app.openapi()
    
    # Записываем схему в JSON файл
    with open("openapi_schema.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    print("OpenAPI спецификация успешно сохранена в openapi_schema.json")

if __name__ == "__main__":
    generate_spec()
