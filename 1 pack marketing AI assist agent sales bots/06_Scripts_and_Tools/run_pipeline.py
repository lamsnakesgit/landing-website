import os
import sys
import subprocess
import threading
import queue
import time
import signal
from loguru import logger

# Игнорируем сигнал SIGHUP для предотвращения прерывания процесса при закрытии терминала в macOS
try:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
except AttributeError:
    pass

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/pipeline_run.log", rotation="10 MB", retention="7 days", level="INFO")

def run_step(command, description, timeout=2100):
    """Вспомогательная функция для запуска шага в терминале с таймаутом (по умолчанию 35 минут)"""
    logger.info(f"=== Запуск: {description} ===")
    logger.info(f"Команда: {command}")
    
    try:
        # Запуск процесса с перенаправлением вывода
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Очередь для хранения вывода процесса
        q = queue.Queue()
        
        # Поток для неблокирующего чтения stdout/stderr процесса
        def read_output(stream, out_queue):
            for line in stream:
                out_queue.put(line)
            stream.close()
            
        reader_thread = threading.Thread(target=read_output, args=(process.stdout, q))
        reader_thread.daemon = True
        reader_thread.start()
        
        start_time = time.time()
        
        while True:
            # Проверка превышения таймаута
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.error(f"❌ Превышен лимит времени выполнения ({timeout} сек) для шага: {description}. Принудительно убиваем процесс...")
                process.kill()
                process.wait()
                return False
                
            # Выводим все строки, поступившие в очередь
            while not q.empty():
                try:
                    line = q.get_nowait()
                    try:
                        sys.stdout.write(line)
                        sys.stdout.flush()
                        clean_line = line.strip()
                        if clean_line:
                            logger.info(f"[{description}]: {clean_line}")
                    except (BrokenPipeError, OSError):
                        pass
                except queue.Empty:
                    break
            
            # Если процесс завершился, выходим из цикла ожидания
            if process.poll() is not None:
                # Читаем оставшийся в очереди вывод
                while not q.empty():
                    try:
                        line = q.get_nowait()
                        try:
                            sys.stdout.write(line)
                            sys.stdout.flush()
                            clean_line = line.strip()
                            if clean_line:
                                logger.info(f"[{description}]: {clean_line}")
                        except (BrokenPipeError, OSError):
                            pass
                    except queue.Empty:
                        break
                break
                
            time.sleep(0.2)
            
        if process.returncode == 0:
            logger.success(f"Успешно завершено: {description}")
            return True
        else:
            logger.error(f"Ошибка при выполнении: {description} (Код возврата: {process.returncode})")
            return False
            
    except Exception as e:
        logger.error(f"Исключение при выполнении {description}: {e}")
        return False

def cleanup_old_data(retention_days=7):
    """Очистка старых логов и папок с лидами для предотвращения переполнения диска"""
    logger.info("=== Запуск очистки старых данных (ротация) ===")
    
    from datetime import datetime, timedelta
    import shutil
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    # 1. Очистка старых папок daily_leads
    leads_dir = "03_Marketing_and_Sales/daily_leads"
    if os.path.exists(leads_dir):
        for item in os.listdir(leads_dir):
            item_path = os.path.join(leads_dir, item)
            if os.path.isdir(item_path):
                try:
                    folder_date = datetime.strptime(item, "%Y-%m-%d")
                    if folder_date < cutoff_date:
                        logger.info(f"Удаляем старую папку с лидами: {item_path}")
                        try:
                            shutil.rmtree(item_path)
                        except Exception as e:
                            logger.error(f"Не удалось удалить папку {item_path}: {e}")
                except ValueError:
                    pass

    # 2. Очистка/усечение неконтролируемых логов в logs/
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        for log_file in os.listdir(logs_dir):
            log_path = os.path.join(logs_dir, log_file)
            if os.path.isfile(log_path):
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
                    if mtime < cutoff_date:
                        logger.info(f"Удаляем старый лог-файл: {log_path}")
                        os.remove(log_path)
                    elif os.path.getsize(log_path) > 10 * 1024 * 1024:
                        logger.info(f"Лог-файл {log_path} превышает 10МБ. Усекаем его...")
                        with open(log_path, "w") as f:
                            f.write(f"--- Log truncated at {datetime.now()} ---\n")
                except Exception as e:
                    logger.error(f"Не удалось обработать лог {log_path}: {e}")

def main():
    # Проверка на повторный запуск в тот же день
    force_run = "--force" in sys.argv
    date_str = datetime.now().strftime("%Y-%m-%d")
    last_run_file = "logs/.last_run"
    
    if not force_run and os.path.exists(last_run_file):
        try:
            with open(last_run_file, "r", encoding="utf-8") as f:
                last_run_date = f.read().strip()
            if last_run_date == date_str:
                logger.info(f"📅 Сбор контактов на сегодня ({date_str}) уже выполнялся. Пайплайн завершен. Используйте --force для принудительного запуска.")
                print(f"Сбор на сегодня ({date_str}) уже был выполнен ранее. Пропуск.")
                sys.exit(0)
        except Exception as e:
            logger.warning(f"Не удалось прочитать файл последнего запуска: {e}")

    try:
        cleanup_old_data(retention_days=7)
    except Exception as e:
        logger.error(f"Ошибка при очистке старых данных: {e}")

    logger.info("⚡ Начинаем выполнение полного пайплайна лидогенерации...")
    
    quick_mode = "--quick" in sys.argv
    
    # Шаг 1. Сбор свежих лидов с HH.ru, HH.kz, Adata.kz и Threads.net с помощью Playwright
    python_bin = sys.executable
    playwright_flags = " --quick" if quick_mode else ""
    playwright_cmd = f'"{python_bin}" scripts/playwright_leadgen.py{playwright_flags}'
    step1_success = run_step(playwright_cmd, "Сбор лидов через Playwright (HH + Adata + Threads)")
    
    # Шаг 1.5. Сбор судебных дел из Судебного кабинета по трудовым спорам
    court_parser_cmd = f'"{python_bin}" scripts/sud_parser/parser_tk.py'
    step1_5_success = run_step(court_parser_cmd, "Сбор судебных дел (office.sud.kz)")
    
    if not step1_5_success:
        logger.warning("⚠️ Не удалось собрать судебные дела (возможно, устарела сессия), продолжаем без них...")

    # Шаг 2. ИИ-обогащение, генерация оферов, драфтов сообщений и отправка отчетов
    leadgen_flags = " --limit=2" if quick_mode else ""
    leadgen_cmd = f'"{python_bin}" 06_Scripts_and_Tools/daily_leadgen.py{leadgen_flags}'
    step2_success = run_step(leadgen_cmd, "ИИ-обогащение, генерация офферов и отправка отчетов")
    
    if step2_success:
        logger.success("🎉 Полный пайплайн лидогенерации успешно завершен!")
        try:
            with open(last_run_file, "w", encoding="utf-8") as f:
                f.write(date_str)
            logger.info(f"Записана дата успешного запуска: {date_str}")
        except Exception as e:
            logger.error(f"Не удалось записать дату запуска в {last_run_file}: {e}")
    else:
        logger.error("❌ Пайплайн завершился с критической ошибкой на этапе обогащения.")

if __name__ == "__main__":
    from datetime import datetime
    main()
