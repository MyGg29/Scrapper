import requests
from bs4 import BeautifulSoup

url = "https://cas.isen.fr/login"
password = "YOURPASSWORDHERE"
username = "YOURUSERNAMEHERE"

with requests.Session() as s:
    r = s.get(url)

    parser = BeautifulSoup(r.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
    payload = {}

    for DOMInput in parser.findAll(name = "input"):
        if DOMInput['name'] == 'lt':
            payload['lt'] = DOMInput['value']                

    payload['username'] = username
    payload['password'] = password
    r = s.post(r.url, params = payload)
