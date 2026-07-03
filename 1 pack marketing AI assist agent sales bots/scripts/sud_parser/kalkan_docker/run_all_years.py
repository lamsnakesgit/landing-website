import os
import subprocess
import time

YEARS = list(range(2026, 2014, -1))

def run_parser_for_year(year):
    print(f"\n{'='*50}")
    print(f"🚀 ЗАПУСК ПАРСЕРА ДЛЯ ГОДА: {year}")
    print(f"{'='*50}\n")
    
    # 2. Build image just in case (Skipped due to volume mapping)
    # subprocess.run(["docker", "build", "-t", "kalkan_parser", "."], check=True)
    
    # 3. Run container
    print(f"Running docker container for {year}...")
    result = subprocess.run([
        "docker", "run", "--rm",
        "-e", f"PARSE_YEAR={year}",
        "-v", f"{os.path.abspath('keys')}:/keys",
        "-v", f"{os.path.abspath('output')}:/output",
        "-v", f"{os.path.abspath('sud_parser.py')}:/app/sud_parser.py",
        "kalkan_parser"
    ])
    
    if result.returncode != 0:
        print(f"⚠️ Парсинг года {year} завершился с ошибкой (код {result.returncode})")
    else:
        print(f"✅ Парсинг года {year} успешно завершен")

def main():
    os.makedirs("output", exist_ok=True)
    
    for year in YEARS:
        run_parser_for_year(year)
        print(f"Ожидание 10 секунд перед следующим годом...")
        time.sleep(10)
        
    print("\n🎉 Все года (2026-2015) успешно обработаны!")

if __name__ == "__main__":
    main()
