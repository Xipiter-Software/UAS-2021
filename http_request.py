import requests
import os

URL1 = "http://192.168.1.101:8000/api/login"

  
# defining a params dict for the parameters to be sent to the API
PARAMS1 = {'username':'testuser', 'password':'testpass'}
  
# sending get request and saving the response as response object
r1 = requests.post(url = URL1, json = PARAMS1)
  
cookie = r1.cookies

#print (cookie)

URL2 = "http://192.168.1.101:8000/api/missions/1"

r2 = requests.get(url = URL2, cookies = cookie)

file = open("Mission.json", "w")

file.write(r2.text)

file.close()

print (r2.text)


#cmd = 'sshpass -p "W@tche$" scp Mission.json xipiter@192.168.1.59:/home/xipiter/'

#os.system(cmd)
