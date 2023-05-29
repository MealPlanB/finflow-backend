

import requests
import json
url = 'https://openapivts.koreainvestment.com:29443/'
forToken = '/oauth2/tokenP'
urlToken = url + forToken


APP_KEY = 'PSIZExuxlSzK50wmyUIeI1VWQvvqepe9FeJW'
APP_SECRET = 'IuAtB6vXKnChmNsUkVG5bVqZ13kN/3j1gVYQwn57ruNTvOegy5tKGlaYlInAJYv4Ysb6yuSF64VQJV9b8NOatzZOtLeGuWjgI9UIx4WWceFokBsTFdQ220SVB9gYeEUjPA7qov6uhTcJQay4bqV7xNfWPaf6WMYgGQzWxLFCpeDWd3gDg0c='

CANO: "99122965"







headers = {'content-type' : 'application/json; charset=utf-8',
           'authorization' : "Bearer 8cfb9e28-9362-4f36-b999-5f81ff43d840",
           'appkey' : APP_KEY,
           'appsecret' : APP_SECRET,
           'tr_id' : 'FHKST01010100'
}

data = {'grant_type' : 'client_credentials',
        'appkey' : APP_KEY,
        'appsecret' : APP_SECRET
        }

tokenResponse = requests.post(urlToken, data = json.dumps(data))
print(tokenResponse)

print(tokenResponse.json())





'''
print(url)
print("\n")
response = requests.get(url, headers = headers, params = params)
if response == 200:
    print(response.json())
print(response)
print(response.text)
'''
