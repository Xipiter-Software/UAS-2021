import requests
import os
import time
import json

#URL1 = "http://192.168.1.101:8000/api/login"

  
# defining a params dict for the parameters to be sent to the API
#PARAMS1 = {'username':'testuser', 'password':'testpass'}
  
# sending get request and saving the response as response object
#r1 = requests.post(url = URL1, json = PARAMS1)
  
#cookie = r1.cookies

#print (cookie)

#URL2 = "http://192.168.1.101:8000/api/missions/1"

#r2 = requests.get(url = URL2, cookies = cookie)

#file = open("Mission.json", "w")

#file.write(r2.text)

#file.close()

#print (r2.text)


#cmd = 'sshpass -p "W@tche$" scp Mission.json xipiter@192.168.1.59:/home/xipiter/'

#os.system(cmd)

def setServerInfo(interopIP_Address = None, username = None, password = None, infoFile = None):
	pass
	#this function should make a request to the ground station for input
	#the infoFile param is for possible implementation of an auto-startup upon disconnect

def interopConnect(interopIP_Address, username, password, timeout = 10):

	loginURL = "http://" + str(interopIP_Address) + "/api/login"
	logincreds = {'username':str(username), 'password':str(password)}

	for i in range(timeout):
		loginRequest = requests.post(url = loginURL, json = logincreds)
		time.sleep(1)
		#arbitrary wait time for server request

		if("200" in loginRequest.text):
			#upon successful request
			loginCookie = loginRequest.cookies
			return loginCookie

	#should raise an exception for login request not managed

def getMission(interopIP_Address, missionID, loginCookie, timeout = 10):

	missionURL = "http://" + str(interopIP_Address) + "/api/missions/" + str(missionID)

	for i in range(timeout):
		missionRequest = requests.get(url = missionURL, cookies = loginCookie)
		time.sleep(1)
		#arbitrary wait time for server request

		if("200" in missionRequest.text):
			#upon successful request
			mission = missionRequest.text
			mission.strip("\n\t ")			
			
			return mission

	#should raise an exception for login request not managed

def getFlightBounds(mission):
	indx = mission.index("\"flyZones\"")
	boundsSegmt = mission[mission.index("[", indx) +1 : mission.index("]", indx + mission.index("]", indx))]
	"""
	"flyZones": [ <<< STARTS HERE <<<
	    {
	      "altitudeMin": 100.0,
	      "altitudeMax": 750.0,
	      "boundaryPoints": [
		{
		  "latitude": 38.1462694444444,
		  "longitude": -76.4281638888889
		},
		/// omitted elements ///
		{
		  "latitude": 38.1461305555556,
		  "longitude": -76.4266527777778
		}
	      ]
	    }
	  ] <<< ENDS HERE <<<
	"""
	
	indx = boundsSegmt.index("\"altitudeMin\":") +len("\"altitudeMin\":") +1
	altitudeMin = boundsSegmt[indx : boundsSegmt.index(",", indx)]
	altitudeMin = float(altitudeMin)
	#isolates minimum flight altitude from flyZones segment

	indx = boundsSegmt.index("\"altitudeMax\":") +len("\"altitudeMax\":") +1
	altitudeMax = boundsSegmt[indx : boundsSegmt.index(",", indx)]
	altitudeMax = float(altitudeMax)
	#isolates maximum flight altitude from flyZones segment
	
	bounds = splitJSON(boundsSegmt)
	#reduces string to list of latitude & longitude segments
	
	flightBounds = list()
	bounds = [point.split(",") for point in bounds]
	
	for l in bounds:
		l[0] = float( l[0][len("\"latitude\":")+1:] )
		l[1] = float( l[1][len("\"longitude\":")+1:] )

		flightBounds.append(tuple((l[0], l[1])))
	
	return tuple((altitudeMin, altitudeMax, fligtBounds))

def splitJSON(string):
	indx = string.index("[") +1
	endIndx = string.index("]")
	splitJSON = string[indx : endIndx]
	splitJSON = splitJSON.strip("{")
	splitJSON = splitJSON.split("},")
	
	return splitJSON

def getWaypoints(mission):
	indx = mission.index("\"waypoints\"")
	waypoints = mission[mission.index("[", indx) +1 : mission.index("]", indx)]
	
	waypoints = splitJSON(waypoints)
	#reduces string to list of latitude & longitude segments
	
	flightPoints = list()
	waypoints = [point.split(",") for point in waypoints]
	
	for l in waypoints:
		l[0] = float( l[0][len("\"latitude\":")+1:] )
		l[1] = float( l[1][len("\"longitude\":")+1:] )
		l[2] = float( l[2][len("\"altitude\":")+1:] )

		flightPoints.append(tuple((l[0], l[1], l[2])))
	
	return tuple(flightPoints)

def getSearchGridPoints(mission):
	indx = mission.index("\"searchGridPoints\"")
	gridPoints = mission[mission.index("[", indx) +1 : mission.index("]", indx)]
	
	gridPoints = splitJSON(gridPoints)
	#reduces string to list of latitude & longitude segments
	
	searchPoints = list()
	gridPoints = [point.split(",") for point in gridPoints]
	
	for l in gridPoints:
		l[0] = float( l[0][len("\"latitude\":")+1:] )
		l[1] = float( l[1][len("\"longitude\":")+1:] )

		searchPoints.append(tuple((l[0], l[1])))
	
	return tuple(searchPoints)

def getAirDropDetails(mission): #should utilize a namedTuple
	indx = mission.index("\"airDropBoundaryPoints\"")
	bounds = mission[mission.index("[", indx) +1 : mission.index("]", indx)]
	
	bounds = splitJSON(bounds)
	#reduces string to list of latitude & longitude segments
	
	airDropBounds = list() #<<<
	bounds = [point.split(",") for point in bounds]
	
	for l in bounds:
		l[0] = float( l[0][len("\"latitude\":")+1:] )
		l[1] = float( l[1][len("\"longitude\":")+1:] )

		airDropBounds.append(tuple((l[0], l[1])))
	##################
	indx = mission.index("\"airDropPos\"")
	landingSpot = mission[mission.index("{", indx) +1 : mission.index("}", indx)]
	landingSpot = landingSpot.split(",")
	
	landingSpot[0] = float( landingSpot[0][len("\"latitude\":")+1:] )
	landingSpot[1] = float( landingSpot[1][len("\"longitude\":")+1:] )
	ugvLandingPos = tuple((landingSpot[0], landingSpot[1])) #<<<
	##################
	indx = mission.index("\"ugvDrivePos\"")
	driveSpot = mission[mission.index("{", indx) +1 : mission.index("}", indx)]
	driveSpot = driveSpot.split(",")
	
	driveSpot[0] = float( driveSpot[0][len("\"latitude\":")+1:] )
	driveSpot[1] = float( driveSpot[1][len("\"longitude\":")+1:] )
	ugvDrivePos = tuple((driveSpot[0], driveSpot[1])) #<<<

	return tuple((airDropBounds, ugvLandingPos, ugvDrivePos))

def getStaticObstacles(mission):
	indx = mission.index("\"stationaryObstacles\"")
	objct = mission[mission.index("[", indx) +1 : mission.index("]", indx)]
	
	objct = splitJSON(objct)
	#reduces string to list of latitude & longitude segments
	
	obstacles = list()
	objct = [point.split(",") for point in objct]
	
	for l in objct:
		l[0] = float( l[0][len("\"latitude\":")+1:] )
		l[1] = float( l[1][len("\"longitude\":")+1:] )
		l[2] = float( l[0][len("\"radius\":")+1:] )
		l[3] = float( l[1][len("\"height\":")+1:] )

		obstacles.append(tuple((l[0], l[1], l[2], l[3])))
	
	return tuple(obstacles)

def getKnownObjectPos(mission): #should utilize a namedTuple
	indx = mission.index("\"lostCommsPos\"")
	commsPos = mission[mission.index("{", indx) +1 : mission.index("}", indx)]
	commsPos = commsPos.split(",")
	
	commsPos[0] = float( commsPos[0][len("\"latitude\":")+1:] )
	commsPos[1] = float( commsPos[1][len("\"longitude\":")+1:] )
	lostCommsPos = tuple((commsPos[0], commsPos[1])) #<<<
	##################
	indx = mission.index("\"offAxisOdlcPos\"")
	outerObjct = mission[mission.index("{", indx) +1 : mission.index("}", indx)]
	outerObjct = outerObjct.split(",")
	
	outerObjct[0] = float( outerObjct[0][len("\"latitude\":")+1:] )
	outerObjct[1] = float( outerObjct[1][len("\"longitude\":")+1:] )
	offAxisOdlcPos = tuple((outerObjct[0], outerObjct[1])) #<<<
	##################
	indx = mission.index("\"emergentLastKnownPos\"")
	emergentLastPos = mission[mission.index("{", indx) +1 : mission.index("}", indx)]
	emergentLastPos = emergentLastPos.split(",")
	
	emergentLastPos[0] = float( emergentLastPos[0][len("\"latitude\":")+1:] )
	emergentLastPos[1] = float( emergentLastPos[1][len("\"longitude\":")+1:] )
	emergentLastKnownPos = tuple((emergentLastPos[0], emergentLastPos[1])) #<<<

	return tuple((lostCommsPos, offAxisOdlcPos, emergentLastKnownPos))

def getMapDetails(mission): #should utilize a namedTuple
	indx = mission.index("\"mapCenterPos\"")
	mapCenter = mission[mission.index("{", indx) +1 : mission.index("}", indx)]
	mapCenter = mapCenter.split(",")
	
	mapCenter[0] = float( mapCenter[0][len("\"latitude\":")+1:] )
	mapCenter[1] = float( mapCenter[1][len("\"longitude\":")+1:] )
	mapCenterPos = tuple((mapCenter[0], mapCenter[1])) #<<<

	indx = mission.index("\"mapHeight\"")
	mapHeight = mission[mission.index(":", indx) +1 : mission.index("}", indx)]
	mapHeight = float(mapHeight)

	return tuple((mapCenterPos, mapHeight))

def getOtherPlanePos(interopIP_Address, loginCookie, timeout = 10):
	teamsURL = "http://" + str(interopIP_Address) + "/api/teams"
	pass
	#TODO: parse teams json list and return lat, lon, and alt as tuple of tuples
