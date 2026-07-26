import urllib.request
import csv

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmC-QQ03ItAK2coEnsW6CQpzl8RmSjsxCfff9ylX3BK0cX1Dwbf82nFN3w7TRjzICjoY1xtvaB9dRz/pub?output=csv"
print("Downloading data...")
response = urllib.request.urlopen(url)
lines = [l.decode('utf-8') for l in response.readlines()]
reader = csv.reader(lines)
header = next(reader)
rows = list(reader)

print("Rows:", len(rows))
print("Columns:", header)
print("First 3 rows:")
for r in rows[:3]:
    print(r)
