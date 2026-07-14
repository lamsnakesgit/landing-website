import os
import sys
import subprocess
from loguru import logger

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/scheduler_setup.log", rotation="10 MB", retention="7 days", level="INFO")

def setup_mac_scheduler():
    """Создает wrapper-скрипт и регистрирует LaunchAgent plist для ежедневного запуска лидогенерации через osascript"""
    logger.info("Начинаю настройку планировщика launchd для macOS...")
    
    # Пути
    project_dir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
    python_path = os.path.join(project_dir, ".venv/bin/python")
    run_pipeline_path = os.path.join(project_dir, "06_Scripts_and_Tools/run_pipeline.py")
    
    user_home = os.path.expanduser("~")
    wrapper_path = os.path.join(user_home, "run_daily_pipeline_wrapper.sh")
    
    # 1. Создаем/обновляем wrapper-скрипт в домашней папке для обхода ограничений TCC
    wrapper_content = f"""#!/bin/zsh
# Обертка для запуска ежедневного сбора контактов из домашней папки, чтобы обойти ограничения TCC macOS
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
cd "{project_dir}"

echo "=== [$(date)] Запуск ежедневного сбора контактов ==="

# Запуск основного оркестратора пайплайна
"{python_path}" "{run_pipeline_path}"
STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo "$(date): Ошибка при выполнении пайплайна. Код выхода: $STATUS"
  exit $STATUS
fi

echo "$(date): === Конвейер daily_leadgen успешно завершен! ==="
"""
    try:
        with open(wrapper_path, "w", encoding="utf-8") as f:
            f.write(wrapper_content)
        subprocess.run(["chmod", "+x", wrapper_path], check=True)
        logger.info(f"Wrapper-скрипт успешно создан и помечен как исполняемый по пути: {wrapper_path}")
    except Exception as e:
        logger.error(f"Не удалось создать wrapper-скрипт: {e}")
        return False

    plist_label = "com.higherpower.daily_leadgen"
    launch_agents_dir = os.path.join(user_home, "Library/LaunchAgents")
    
    os.makedirs(launch_agents_dir, exist_ok=True)
    plist_path = os.path.join(launch_agents_dir, f"{plist_label}.plist")
    
    # 2. Создаем plist-файл, запускающий wrapper через osascript для обхода TCC
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{plist_label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>open</string>
        <string>-a</string>
        <string>Terminal</string>
        <string>{wrapper_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{user_home}/Library/Logs/{plist_label}.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>{user_home}/Library/Logs/{plist_label}.stderr.log</string>
</dict>
</plist>
"""
    
    # Записываем plist файл
    try:
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(plist_content)
        logger.info(f"Файл plist успешно создан по пути: {plist_path}")
    except Exception as e:
        logger.error(f"Не удалось записать plist файл: {e}")
        return False
        
    # Регистрируем в launchd
    try:
        # Сначала выгрузим старый агент, если он был загружен (проверим оба возможных названия)
        subprocess.run(["launchctl", "unload", plist_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        old_plist_path = os.path.join(launch_agents_dir, "com.higherpower.leadgen.plist")
        if os.path.exists(old_plist_path):
            subprocess.run(["launchctl", "unload", old_plist_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                os.remove(old_plist_path)
                logger.info("Удален устаревший com.higherpower.leadgen.plist")
            except Exception:
                pass
        
        # Загружаем новый
        result = subprocess.run(["launchctl", "load", plist_path], capture_output=True, text=True)
        if result.returncode == 0:
            logger.success(f"Агент {plist_label} успешно зарегистрирован в launchd!")
            print(f"\n\u2705 Планировщик launchd успешно настроен!")
            print(f"Сбор будет запускаться каждый день в 09:00.")
            print(f"Логи выполнения будут доступны в:\n- {user_home}/Library/Logs/{plist_label}.stdout.log\n- {user_home}/Library/Logs/{plist_label}.stderr.log")
            return True
        else:
            logger.error(f"Ошибка регистрации агента в launchctl: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Исключение при работе с launchctl: {e}")
        return False

if __name__ == "__main__":
    setup_mac_scheduler()
