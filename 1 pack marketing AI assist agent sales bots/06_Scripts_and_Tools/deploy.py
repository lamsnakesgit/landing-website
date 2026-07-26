import paramiko
import os
import sys
import time

host = '151.244.228.104'
port = 22
user = 'root'
password = 'g2AjLzx1drew4ozpArNe'

base_local = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scripts/sud_parser/kalkan_docker'
base_remote = '/root/ai_lawyer/kalkan_docker'

max_retries = 3
for attempt in range(max_retries):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to VPS... (Attempt {attempt+1})")
        ssh.connect(host, port, user, password, timeout=60, banner_timeout=200)
        
        print("Opening SFTP...")
        sftp = ssh.open_sftp()
        
        try:
            sftp.mkdir(f"{base_remote}/lib")
        except:
            pass
            
        print("Uploading libs...")
        sftp.put(os.path.join(base_local, 'lib', 'libkalkancryptwr-64.so.2.0.2'),
                 os.path.join(base_remote, 'lib', 'libkalkancryptwr-64.so.2.0.2'))

        files_to_upload = [
            'Dockerfile', 
            'auth_kalkan.py', 
            'sud_parser.py', 
            'search_cases.py',
            'kalkan_sign.c', 
            'KalkanCrypt.h'
        ]
        for fname in files_to_upload:
            print(f"Uploading {fname}...")
            sftp.put(os.path.join(base_local, fname), os.path.join(base_remote, fname))

        # Загружаем корневые сертификаты НУЦ РК
        certs_local = os.path.join(base_local, 'certs')
        certs_remote = f"{base_remote}/certs"
        try:
            sftp.mkdir(certs_remote)
        except:
            pass
        import glob
        for cert_file in glob.glob(os.path.join(certs_local, '*')):
            fname_c = os.path.basename(cert_file)
            print(f"Uploading cert {fname_c}...")
            sftp.put(cert_file, f"{certs_remote}/{fname_c}")
        
        sftp.close()
        
        # Папка для output на VPS
        ssh.exec_command('mkdir -p /root/ai_lawyer/output')
        time.sleep(1)

        print("Building Docker image (с кешем — быстро)...")
        build_cmd = f'cd {base_remote} && docker build -t kalkan_parser . 2>&1'
        _, stdout_b, _ = ssh.exec_command(build_cmd, get_pty=True)
        for line in stdout_b:
            print(line, end="")

        # Быстрый апдейт скрипта без пересборки: копируем в контейнер напрямую
        # (работает если образ уже собран с нужными зависимостями)
        inject_cmd = (
            f'docker create --name tmp_inject kalkan_parser && '
            f'docker cp {base_remote}/sud_parser.py tmp_inject:/app/sud_parser.py && '
            f'docker commit tmp_inject kalkan_parser && '
            f'docker rm tmp_inject'
        )
        _, out_inject, _ = ssh.exec_command(inject_cmd, get_pty=True)
        print(out_inject.read().decode())
        print("✅ sud_parser.py обновлён в образе без пересборки")

        print("\nRunning parser...")
        run_cmd = (
            f'docker run --rm '
            f'-v /root/ai_lawyer/keys:/keys '
            f'-v /root/ai_lawyer/output:/output '
            f'-e ECP_PASSWORD="Prioritize_resource3!" '
            f'kalkan_parser'
        )
        _, stdout_r, stderr_r = ssh.exec_command(run_cmd, get_pty=True)
        for line in stdout_r:
            print(line, end="")
        for line in stderr_r:
            print(line, file=sys.stderr, end="")

        # Скачиваем результат
        print("\nDownloading results...")
        try:
            sftp2 = ssh.open_sftp()
            sftp2.get('/root/ai_lawyer/output/labor_cases.json', '/tmp/labor_cases.json')
            try:
                sftp2.get('/root/ai_lawyer/output/search_debug.html', '/tmp/search_debug.html')
                sftp2.get('/root/ai_lawyer/output/case_debug.xml', '/tmp/case_debug.xml')
            except:
                pass
            import json
            with open('/tmp/labor_cases.json', 'r') as f:
                data = json.load(f)
            print(f"✅ Найдено дел: {len(data)}")
            print(f"✅ Результаты: /tmp/labor_cases.json")
            
            # Пытаемся скачать HTML страницы, если они есть
            import stat
            for attr in sftp2.listdir_attr('/root/ai_lawyer/output/'):
                if attr.filename.endswith(".html"):
                    sftp2.get(f"/root/ai_lawyer/output/{attr.filename}", f"/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/{attr.filename}")
                    print(f"✅ Скачан HTML: output/{attr.filename}")
                    
            # Скачиваем PDF
            try:
                local_pdf_dir = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/pdfs'
                os.makedirs(local_pdf_dir, exist_ok=True)
                for attr in sftp2.listdir_attr('/root/ai_lawyer/output/pdfs/'):
                    if attr.filename.endswith(".pdf"):
                        sftp2.get(f"/root/ai_lawyer/output/pdfs/{attr.filename}", os.path.join(local_pdf_dir, attr.filename))
                        print(f"✅ Скачан PDF: {attr.filename}")
            except Exception as e:
                print(f"⚠️  Нет PDF файлов или ошибка: {e}")
                
            sftp2.close()
        except Exception as e:
            print(f"⚠️  Не удалось скачать results: {e}")
            
        ssh.close()
        print("Deployment completed.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
