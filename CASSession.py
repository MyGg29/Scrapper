import requests
from bs4 import BeautifulSoup        

class CASSession:

    url = "https://cas.isen.fr/login"
    password = None
    username = None

    def __init__(self):
        print("Initiating CASSession object")

    def getSession(self):
        if self.password == None or self.username == None:
            raise Exception("Missing password or username !")
        reqSession = requests.Session()
        response = reqSession.get(self.url)

        parser = BeautifulSoup(response.text.encode(encoding='UTF-8',errors='strict'), 'html.parser')
        payload = {}

        for DOMInput in parser.findAll(name = "input"):
            if DOMInput['name'] == 'lt':
                payload['lt'] = DOMInput['value']

        payload['username'] = self.username
        payload['password'] = self.password
        response = reqSession.post(response.url, params = payload)
        return reqSession

    def setUsername(self, newUsername):
        self.username = newUsername

    def setPassword(self, newPassword):
        self.password = newPassword

    def __enter__(self):
        self.session = self.getSession()
        return self.session

    def __exit__(self, type, value, traceback):
        self.session.close()
