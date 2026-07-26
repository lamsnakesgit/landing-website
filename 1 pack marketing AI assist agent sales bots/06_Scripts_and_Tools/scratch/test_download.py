import requests
import re

FILE_ID = "1tQffcQIeutV3HysRdF0KGIda6O_5dqoT"
URL = "https://docs.google.com/uc?export=download"

session = requests.Session()
response = session.get(URL, params={'id': FILE_ID})

print("Status code:", response.status_code)
print("Length of response text:", len(response.text))

# Ищем форму с действием (action) и её скрытыми полями
# Пример: action="https://drive.usercontent.google.com/download"
action_match = re.search(r'action="([^"]+)"', response.text)
if action_match:
    action_url = action_match.group(1)
    print("Action URL:", action_url)
else:
    print("Action URL not found")

# Найдём все <input type="hidden" name="..." value="...">
inputs = re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]+)"', response.text)
print("Inputs:", inputs)
