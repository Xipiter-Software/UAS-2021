import time
import requests
import json

#maybe include a subclass ODLC to store classified objects to add functionality for identifying input fields left black

#https://requests.readthedocs.io/en/latest/api/

#https://github.com/suas-competition/interop

class InteropServer():
    """
    An interop server class housing the functionality for posting & getting information from the 
    server through http requests.

    Attributes:
        user- (String) Username provided to login to the interop server

        password- (String) Password provided to login to the interop server

        IP_Address- (String) the URL scheme, IP address for the server & access port

        missionID- (int) competition provided mission ID number

        LoginCookie- (Cookie) credentials cookie for continued connection to interp server

    Methods:
        getMission()

        getTeams()

        postTelemetry(dictionary)

        postODLC(dictionary)- posts the provided object classification JSON dictionary to the interop server
            Returns the odlc dictionary provided, modified to include its ID attribute

        putODLC(dictionary, int_ID)- updates the specified (via submitted id) object classification with the provided JSON dictionary
            Returns the updated odlc JSON dictionary 

        getODLC(int_ID)- Returns a list of posted odlc dictionaries, filterable by mission ID with the optional int parameter

        postODLC_Image(int_ID, imageFilePath)- Posts the image binary for the specified object via the provided ID, image type must be JPEG or PNG < 1 MB

        getODLC_Image(int_ID)- Returns the image binary for the odlc object specified by the provided ID

        postMap_Image(int_ID, mapFilePath)- Posts the image binary for map of the provided mission ID, map image type must be JPEG or PNG, < 1 MB, 16:9 aspect ratio, and be WGS 84 Web Mercator Projection

        getMap_Image(int_ID)- Returns the map image binary for the provided mission ID

    """

    def __init__(self, IP, username, password, missionID=1):
        """
        Constructor for interop server objects, establishes connection with the provided IP & server

        Params:
            IP- (String) IP address for the server, including port; ex: 127.0.0.1:8008
            
            username- (String) competition provided username

            password- (String) competition provided password

            missionID- (int) competition provided mission ID number
        """

        self.IP_Address = 'http://' + IP
        self.user = username
        self.password = password
        self.missionID = missionID

        loginURL = self.IP_Address + "/api/login"
        logincreds = {'username': str(username), 'password': str(password)}


        #look through requests doc for handling requests & validation, 200 code for successful request
        loginRequest = requests.post(url=loginURL, json=logincreds)
        time.sleep(1)
        self.loginCookie = loginRequest.cookies
    

    def getMission(self):
        """
        Fetches and returns the mission JSON from the interop server as a dictionary object
        """

        missionURL = self.IP_Address + "/api/missions/" + str(self.missionID)

        #look through requests doc for handling requests & validation, 200 code for successful request
        missionRequest = requests.get(url=missionURL, cookies=self.loginCookie)
        time.sleep(1)
        
        return json.loads(missionRequest)

    
    def getTeams(self):
        """
        Fetches and returns the teams status JSON from the interop server as a dictionary object
        """

        teamsGetURL = self.IP_Address + "/api/teams"
        #look through requests doc for handling requests & validation, 200 code for successful request
        teamsJSON = requests.get(url=teamsGetURL, cookies=self.loginCookie)
        time.sleep(1)

        return json.loads(teamsJSON)
    

    def postTelemetry(self, telemetry):
        """
        Posts the provided telemetry data to the interop server

        Params:
            telemetry- (Dictionary) telemetry dictionary containing lat., lon., alt., and heading
        """

        telemPostURL = self.IP_Address + "/api/telemetry"
        #look through requests doc for handling requests & validation, 200 code for successful request
        requests.post(url=telemPostURL, json=telemetry, cookies=self.loginCookie)
        time.sleep(1)
    

    def postODLC(self, odlc):
        """
        Posts the provided object classification JSON dictionary to the interop server

        Params:
            odlc- (dictionary) object classification dictionary
        
        Returns:
            (dictionary) the odlc JSON dictionary with asigned ID included as an attribute
        """

        odlcPostURL = self.IP_Address + "/api/odlcs"
        #look through requests doc for handling requests & validation, 200 code for successful request
        odlcJSON = requests.post(url=odlcPostURL, json=odlc, cookies=self.loginCookie)
        time.sleep(1)

        return json.loads(odlcJSON)


    def putODLC(self, odlc, id):
        """
        Puts the provided object classification JSON dictionary to the interop server, replacing the previous odlc via provided ID

        Params:
            odlc- (dictionary) object classification dictionary

            id- (int) id for the specific odlc
        
        Returns:
            (dictionary) the odlc JSON dictionary with ID included as an attribute
        """

        odlcPutURL = self.IP_Address + "/api/odlcs/" + str(id)
        #look through requests doc for handling requests & validation, 200 code for successful request
        odlcJSON = requests.put(url=odlcPutURL, json=odlc, cookies=self.loginCookie)
        time.sleep(1)

        return json.loads(odlcJSON)


    def getODLCs(self, missionFilter=None):
        """
        Gets a list of the previously posted ODLCs, filterable by mission ID

        Params:
            missionFilter- (int) mission ID for filtering returned ODLCs in dictionary JSON list
        
        Returns:
            (dictionary) previously posted ODLCs in a JSON dictionary
        """

        odlcGetURL = self.IP_Address + "/api/odlcs/"

        if isinstance(missionFilter, int):
            odlcGetURL += str(missionFilter)

        #look through requests doc for handling requests & validation, 200 code for successful request
        odlcJSONs = requests.get(url=odlcGetURL, cookies=self.loginCookie)
        time.sleep(1)

        return json.loads(odlcJSONs)
    

    def postODLC_Image(self, id, imagePath):
        """
        Posts the image binary for the specified ODLC via its ID

        Params:
            id- (int) ODLC id

            imagePath- (String) file path for the image representing the ODLC JSON
        """

        with open(imagePath, 'rb') as file:
            imageBinary = file.read()

        odlcPostURL = self.IP_Address + "/api/odlcs/" + str(id) + "/image"
        #look through requests doc for handling requests & validation, 200 code for successful request
        requests.post(url=odlcPostURL, data=imageBinary, cookies=self.loginCookie)
        time.sleep(1)
    

    def getODLC_Image(self, id):
        """
        Gets the image binary for the specified ODLC via its ID

        Params:
            id- (int) ODLC id

        Returns:
            (image binary) the binary for the specified ODLC's image
        """

        odlcGetURL = self.IP_Address + "/api/odlcs/" + str(id) + "/image"
        #look through requests doc for handling requests & validation, 200 code for successful request
        imageBinary = requests.get(url=odlcGetURL, cookies=self.loginCookie)
        time.sleep(1)

        return imageBinary
    

    def postMap_Image(self, id, mapPath):
        """
        Posts the map image binary for the specified mission via its ID

        Params:
            id- (int) mission id

            mapPath- (String) file path for the mission map
        """

        with open(mapPath, 'rb') as file:
            mapBinary = file.read()

        mapPostURL = self.IP_Address + "/api/maps/" + str(id) + "/" + str(self.user)
        #look through requests doc for handling requests & validation, 200 code for successful request
        requests.post(url=mapPostURL, data=mapBinary, cookies=self.loginCookie)
        time.sleep(1)
    

    def getMap_Image(self, id):
        """
        Gets the map image binary for the specified mission via its ID

        Params:
            id- (int) mission id

        Returns:
            (image binary) the binary for the specified mission's map
        """

        mapGetURL = self.IP_Address + "/api/maps/" + str(id) + "/" + str(self.user)
        #look through requests doc for handling requests & validation, 200 code for successful request
        mapBinary = requests.get(url=mapGetURL, cookies=self.loginCookie)
        time.sleep(1)

        return mapBinary
    
    #Excluded deleteODLC_Image(self, id)
    #Excluded deleteMap_Image(self, id)


    #TODO
    def __repr__():
        return "UwU Statwus updwates"

