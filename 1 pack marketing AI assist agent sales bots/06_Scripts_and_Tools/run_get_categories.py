import paramiko
import sys

host = '151.241.100.226'
port = 22
user = 'root'
password = 'r0oLNJP3xCO7O4SnL0bj'

script_content = """
import os
import re
import requests
import html as html_lib
import subprocess
from bs4 import BeautifulSoup

BASE_URL = "https://office.sud.kz"
KEY_PATH = "/keys"
SIGN_BIN = "/app/kalkan_sign"
ECP_PASS = os.environ.get("ECP_PASSWORD", "Prioritize_resource3!")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "text/html"}

def find_key():
    for f in os.listdir(KEY_PATH):
        if f.startswith("GOST") and f.endswith(".p12"):
            return os.path.join(KEY_PATH, f)
    raise FileNotFoundError("Ключ не найден")

def sign_xml(xml_string):
    key = find_key()
    result = subprocess.run([SIGN_BIN, key, ECP_PASS, xml_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
    return result.stdout.strip()

def get_cats():
    session = requests.Session()
    session.verify = False
    import urllib3
    urllib3.disable_warnings()

    resp = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=30)
    html = resp.text
    xml_to_sign = html_lib.unescape(re.search(r'id="xmlToSign0"[^>]*value="([^"]+)"', html).group(1))
    view_state = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html).group(1)
    
    parts = re.search(r'name="(j_idt[^"]*signedXml)"', html).group(1).split(":")
    eds_form = f"{parts[0]}:{parts[1]}"
    signed_field = f"{parts[0]}:{parts[1]}:signedXml"

    signed_xml = sign_xml(xml_to_sign)
    payload = {
        eds_form: eds_form,
        signed_field: signed_xml,
        "javax.faces.ViewState": view_state,
    }
    resp2 = session.post(f"{BASE_URL}/index.xhtml", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30, allow_redirects=True)
    
    # Теперь идем на страницу поиска
    resp_search = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS)
    soup = BeautifulSoup(resp_search.text, 'html.parser')
    
    select = soup.find('select', {'id': 'j_idt35:j_idt40:j_idt41:edit-category'})
    if not select:
        select = soup.find('select', {'id': re.compile(r'edit-category$')})
        
    if select:
        for opt in select.find_all('option'):
            if opt.get('value'):
                print(f"{opt.get('value')} | {opt.text.strip()}")
    else:
        print("Категории не найдены, возможно изменился ID select'a")

if __name__ == "__main__":
    get_cats()
"""

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, user, password, timeout=30)
    
    # Сохраняем скрипт на VPS
    sftp = ssh.open_sftp()
    with sftp.file('/root/ai_lawyer/kalkan_docker/get_cats.py', 'w') as f:
        f.write(script_content)
    sftp.close()

    # Запускаем в докере
    cmd = (
        f'docker run --rm '
        f'-v /root/ai_lawyer/keys:/keys '
        f'-v /root/ai_lawyer/kalkan_docker/get_cats.py:/app/get_cats.py '
        f'-e ECP_PASSWORD="Prioritize_resource3!" '
        f'kalkan_parser python3 /app/get_cats.py'
    )
    print("Выполняю парсинг категорий на сервере...")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    print(out)
    if err:
        print("Errors:", err)
        
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
