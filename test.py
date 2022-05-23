import requests 
import json
import os
directory = "/tmp/"
data = {'grant_type':"client_credentials", 
        'resource':"https://graph.microsoft.com", 
        'client_id':'cf453072-25d9-481e-9164-0895cf7adcfa', 
        'client_secret':'ElF8Q~SUtlbatmVYrJEHWLuiOsiYIk4TNKiLSagd', 'scope' : "Files.ReadWrite.All"} 
#URL = "https://login.windows.net/c6328dc3-afdf-40ce-846d-326eead86d49/oauth2/v2.0/token"
URL = "https://login.windows.net/c6328dc3-afdf-40ce-846d-326eead86d49/oauth2/token?api-version=1.0"
r = requests.post(url = URL, data = data) 
j = json.loads(r.text)
TOKEN = j["access_token"]
URL = "https://graph.microsoft.com/v1.0/users/60c0debd-f5cf-42fd-b6a2-f7317bb7845e/drive/root:/data"
headers={'Authorization': "Bearer " + TOKEN}
r = requests.get(URL, headers=headers)
j = json.loads(r.text)
print (j)
print("Uploading file(s) to "+URL)
fileHandle = open(directory+'prova.txt', 'rb')
r = requests.put(URL+"/"+"prova.txt"+":/content", data=fileHandle, headers=headers)
fileHandle.close()
print (r.status_code)
if r.status_code == 200 or r.status_code == 201:
     print("succeeded!")
print("Script completed")
raise SystemExit
