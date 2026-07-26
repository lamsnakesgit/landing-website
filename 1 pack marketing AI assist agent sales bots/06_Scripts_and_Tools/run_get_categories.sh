#!/bin/bash
export SSHPASS='r0oLNJP3xCO7O4SnL0bj'
cat << 'PYEOF' > get_cats_vps.py
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
    try:
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
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": re.search(r'RichFaces\.ajax\("([^"]+)"', html).group(1),
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "@all",
        }
        payload[payload["javax.faces.source"]] = payload["javax.faces.source"]
        
        resp2 = session.post(f"{BASE_URL}/index.xhtml", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Faces-Request": "partial/ajax"}, timeout=30)
    except Exception as e:
        print("Ошибка авторизации:", e)
        return
        
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
        print("Категории не найдены")

if __name__ == "__main__":
    get_cats()
PYEOF

sshpass -e scp -o StrictHostKeyChecking=no get_cats_vps.py root@151.241.100.226:/root/ai_lawyer/kalkan_docker/get_cats.py
sshpass -e ssh -o StrictHostKeyChecking=no root@151.241.100.226 'docker run --rm -v /root/ai_lawyer/keys:/keys -v /root/ai_lawyer/kalkan_docker/get_cats.py:/app/get_cats.py -e ECP_PASSWORD="Prioritize_resource3!" kalkan_parser python3 /app/get_cats.py'
