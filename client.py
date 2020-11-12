import requests
import json

url = 'http://127.0.0.1:8000'
headers = {'content-type': 'application/json', 'key': 'ziax'}
data = {"sentence": "1 Любая текстовая фраза на русском"}

result = requests.post(url, headers=headers, data=json.dumps(data))

print(result.text)
