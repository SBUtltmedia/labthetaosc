import requests
import json
import shutil
import time
import sys
import pysftp
import os
os.chdir("/usr/local/pictures")

domain = "http://192.168.1.1"
execute = "/osc/commands/execute"
state = "/osc/state"

def callCamera(path, post_data):
	r = requests.post(domain+path, json = post_data)
	return	r.json()



# initial and set API to 2.1
startSession = """
{
	"name": "camera.startSession",
	"parameters": {}
}
"""
post_data1 = json.loads(startSession.replace("\n","").replace(" ",""))

try:
	response = callCamera(execute, post_data1)
	sessionId = response["results"]["sessionId"]
	setAPI = """
{
	"name": "camera.setOptions",
	"parameters": {
		"sessionId": "%s",
		"options": {
			"clientVersion": 2
		}
	}
}
"""%(sessionId)
	post_data2 = json.loads(setAPI.replace("\n","").replace(" ",""))
	callCamera(execute, post_data2)
	print("API has been set to v2.1")
except OSError as err:
	print(("OS error: {0}".format(err)))
except ValueError as err:
	print(("Could not convert data to an integer.".format(err)))
except KeyError:
	print("API is alreay in v2.1")
except:
	print(("Unexpected error:", sys.exc_info()[0]))
	raise





# disable sleep and poweroff and shutter Volume
keepAwake = """
{
        "name": "camera.setOptions",
        "parameters": {
                "options": {
                        "sleepDelay": 65535,
                        "offDelay": 65535,
			"_shutterVolume":0
                }
        }
}
"""
post_data3 = json.loads(keepAwake.replace("\n","").replace(" ",""))
print(callCamera(execute, post_data3))
print("camera will keep awake and quiet")
keepAwake = """
{
        "name": "camera.getOptions",
        "parameters": {
                "optionNames":[ 
                        "sleepDelay"
                ]
        }
}
"""
post_data3 = json.loads(keepAwake.replace("\n","").replace(" ",""))
print(callCamera(execute, post_data3))


# take the picture
takePicture = """
{
	"name": "camera.takePicture"
}
"""
post_data4 = json.loads(takePicture.replace("\n","").replace(" ",""))
callCamera(execute, post_data4)
print("Picture taken")



# store picture in local
isIdle = False # Picture status
checkPicture = """
{
}
"""
post_data5 = json.loads(checkPicture.replace("\n","").replace(" ",""))

while (isIdle == False):
	callCamera(state, post_data5)
	checkPic = callCamera(state, post_data5)
	status = checkPic["state"]["_captureStatus"]
	
	if status == "idle":
		isIdle = True
		fileURL = checkPic["state"]["_latestFileUrl"]
		response = requests.get(fileURL, stream=True)
		with open("lab.jpg", "wb") as out_file:
			shutil.copyfileobj(response.raw, out_file)
			print("Picture saved to local")
		shutil.copyfile("lab.jpg",str(time.time())+".jpg");

# pass the picture to the server
listPicture = """
{
	"name": "camera.listFiles",
	"parameters": {
		"fileType": "all",
		"entryCount": 3,
		"maxThumbSize": 640,
		"_detail": false
		}
}
"""
post_data6 = json.loads(listPicture.replace("\n", "").replace(" ", ""))
callCamera(execute, post_data6)

with pysftp.Connection('129.49.17.154', username='tltsecure', password='******') as sftp:
	with sftp.cd('/var/www/html/Lab'):
		sftp.put("lab.jpg","lab.jpg")  
print("Picture uploaded to server")



# delete the picture
deletePicture = """
{
	"name": "camera.delete",
	"parameters": {
		"fileUrls": ["all"]
		}
}
"""
post_data7 = json.loads(deletePicture.replace("\n","").replace(" ",""))
print(callCamera(execute, post_data7))
print("Picture stash deleted")


