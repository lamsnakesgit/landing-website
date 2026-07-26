from telethon.sync import TelegramClient
from telethon import functions, types
import time
import asyncio

# --- НАСТРОЙКИ ---
API_ID = 34157205  
API_HASH = '8bf47a392c00beb35de64308c827b23b' 

# Впишите номер телефона аккаунта, с которого хотите запустить (с плюсом)
PHONE = '+77771269911' 

# Список групп и постфиксов для добавления в контакты
# Формат: {"название_группы_или_ее_часть": "ваш_постфикс"}
GROUPS_TO_PARSE = {
    "пайдалы": "пайдалы_тараз",
    "zhambyl hub": "zhambyl_hub"
}

DELAY_BETWEEN_ADDS = 30 # Задержка в секундах

# Имя сессии привязываем к номеру, чтобы для разных номеров были разные сессии
session_name = f"session_{PHONE.replace('+', '')}"
client = TelegramClient(session_name, API_ID, API_HASH)

async def main():
    import os
    await client.connect()
    
    if not await client.is_user_authorized():
        if not os.path.exists("code.txt"):
            print("Отправляем запрос на код...")
            try:
                await client.send_code_request(PHONE)
                print("✅ КОД ОТПРАВЛЕН! Проверяйте Telegram и СМС.")
            except Exception as e:
                print(f"❌ Ошибка отправки кода: {e}")
            return
        else:
            with open("code.txt", "r") as f:
                code = f.read().strip()
            print(f"Пытаемся войти с кодом {code}...")
            try:
                await client.sign_in(PHONE, code)
                os.remove("code.txt") # удаляем файл
                print("✅ Успешно вошли в аккаунт!")
            except Exception as e:
                print(f"❌ Ошибка при входе: {e}")
                return
    else:
        print(f"✅ Уже вошли в аккаунт: {PHONE}")
    
    for group_name, postfix in GROUPS_TO_PARSE.items():
        print(f"\n--- Ищем группу: '{group_name}' ---")
        target_group = None
        
        async for dialog in client.iter_dialogs():
            if group_name.lower() in (dialog.name or "").lower():
                target_group = dialog.entity
                break
                
        if not target_group:
            print(f"❌ Группа '{group_name}' не найдена в этом аккаунте. Пропускаем.")
            continue

        print(f"✅ Группа найдена: {target_group.title}")
        print("Получаем список участников...")
        participants = await client.get_participants(target_group)
        print(f"Найдено участников: {len(participants)}")
        
        added_count = 0
        for user in participants:
            if user.bot or user.is_self:
                continue
            
            if user.contact:
                print(f"Пользователь {user.first_name} уже есть в контактах. Пропускаем.")
                continue
                
            first_name = user.first_name or "Без имени"
            last_name = user.last_name or ""
            
            # Формируем новое имя: Имя постфикс
            new_first_name = f"{first_name} {postfix}".strip()
            
            try:
                print(f"Пробуем добавить: {new_first_name} {last_name}...")
                result = await client(functions.contacts.AddContactRequest(
                    id=user.username if user.username else user.id,
                    first_name=new_first_name,
                    last_name=last_name,
                    phone=user.phone or "", 
                    add_phone_privacy_exception=False
                ))
                print(f"✅ Успешно добавлен: {new_first_name} {last_name}")
                added_count += 1
                
                print(f"Ждем {DELAY_BETWEEN_ADDS} секунд...")
                await asyncio.sleep(DELAY_BETWEEN_ADDS)
                
            except Exception as e:
                print(f"❌ Ошибка при добавлении {first_name}: {e}")
                if "FloodWait" in str(e):
                    print("⚠️ Слишком много запросов. Телеграм просит подождать. Останавливаем работу.")
                    return
                await asyncio.sleep(10)

        print(f"🏁 Готово по группе '{group_name}'! Добавлено контактов: {added_count}")

client.loop.run_until_complete(main())
client.disconnect()
