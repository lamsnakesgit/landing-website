import requests

token = '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g'
chat_id = '888005446'
photo_url = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2/hv7o3VgfsairBoQFAawgaQ4cR1m.jpg' # The Matrix DB poster

headers = {'User-Agent': 'Mozilla/5.0'}
image_data = requests.get(photo_url, headers=headers).content

url = f'https://api.telegram.org/bot{token}/sendPhoto'
files = {'photo': ('matrix.jpg', image_data, 'image/jpeg')}
data = {'chat_id': chat_id, 'caption': 'Вот та самая афиша для теста! Закидывай её в воркфлоу 🚀'}

res = requests.post(url, data=data, files=files)
print(res.text)
