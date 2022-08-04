#import statements
import time
import serial
from pymavlink import mavutil
import mavsdk
from mavsdk.geofence import Point, Polygon

import asyncio
import math

import requests

class UAV():
    """
    An Unmanned aerial vehichle class which houses the functionality for
    completeing a waypoint course

    Attributes:
        port- (Serial) reference to the UART serial port for recieving mavlink instructions
        !!! Port must be closed upon termination of connection !!!

        mavlinkConnection- (mavutil) mavlink object for executing low-level commands

        uav- (mavsdk) mavsdk system object for executing high-level commands

        mission- (dictionary) JSON dictionary containing uav mission details

    Methods:
        setMission(dictionary)- sets the class mission attribute

        initFlyZone()- initializes flight bounds & obstacles for uav mission
            Returns False if mission attribute is not set, True otherwsie

        getTelemetryUpdate()- returns the UAV's telemetry data in a dictionary object

        isAutonEnabled()
            Returns True/False whether autonomous mode is enabled by pilot
    
    """

    def __init__(self, baudrate, portName):
        """
        Constructor for UAV class objects: initializes connection with the physical UAV

        Params:
            baudrate- (int) baudrate for serial communication between controllers
            portName- (String) USB port name for serial connection with an onboard computer (running this code)
        """

        #open jetson serial port "/dev/ttyTHS0"
        self.port = serial.Serial(
            port=portName,
            baudrate=baudrate
        )
        time.sleep(0.25)

        #init mavlink connection
        self.mavlinkConnection = mavutil.mavlink_connection(portName, baud=baudrate)
        time.sleep(0.25)

        #initialize & connect to mavsdk object / UAV
        system_address = "serial://" + portName + ":57600"
        self.uav = mavsdk.System()

        asyncio.run(self._initConnection(system_address))


        self.mission = None
        self.telemUpdates = True

        ###self.port.close()
        # !!! must be run upon termination of connection !!!

    async def _initConnection(self, system_address):
        await self.uav.connect(system_address=system_address)


    def setMission(self, mission):
        """
        Sets the mission dictionary for the UAV object, independent from constructor
        for potential connection testing

        Params:
            mission- (dictionary) JSON mission dictonary for uav mission
        """
        self.mission = mission

    
    def initFlyZone(self):
        """
        Initiates upload of geofences for flight bounds & mission obstacles

        Returns: (False) if mission not defined, (True) otherwise
        """
        if self.mission != None:
            asyncio.run(self._initFlightBounds())
            asyncio.run(self._initObstacles())
            return True
        else:
            return False


    async def _initFlightBounds(self):
        flyZone = self.mission["flyZones"]

        maxAlt = flyZone["altitudeMax"]
        minAlt = flyZone["altitudeMin"]

        bounds = flyZone["boundaryPoints"]

        boundPoints = list()
        for point in bounds:
            lat, lon = point.items()
            boundPoints.append(
                Point(lat, lon)
            )

        boundary = Polygon(boundPoints, Polygon.FenceType.INCLUSION)
        await self.uav.geofence.upload_geofence([boundary])
        #use function return for geofence validation & error handling

    async def _initObstacles(self):
        stationaryObstacles = self.mission["stationaryObstacles"]

        obstaclePolygons = list()
        for obstacle in stationaryObstacles:
            lat, lon, rad, height = obstacle.items()
            #mavsdk doesn't seem to have conditional geofences for obstacle height consideration

            obstaclePolygons.append(
                Polygon(self._obstaclePolygon(lat, lon, rad), Polygon.FenceType.EXCLUSION)
            )

        await self.uav.geofence.upload_geofence(obstaclePolygons)
        # use function return for geofence validation & error handling

    #returns a bounding box around circlular obstacles
    def _obstaclePolygon(self, lat, lon, distance):

        # Earth’s radius, sphere
        R = 6378137

        # Coordinate offsets in radians
        dLat = distance / R
        dLon = distance / (R * math.cos(math.pi * lat / 180))

        # OffsetPosition, decimal degrees
        latOffset = math.radians(dLat)
        lonOffset = math.radians(dLon)

        polygon = [
            Point(lat + latOffset, lon + lonOffset),
            Point(lat + latOffset, lon - lonOffset),
            Point(lat - latOffset, lon - lonOffset),
            Point(lat - latOffset, lon + lonOffset)
        ]

        return polygon
    

    def getTelemetryUpdate(self):
        """
        Returns a dictionary containing the UAV's telemetry data
        """

        positionStatus = self.mavlinkConnection.recv_match(type='GLOBAL_POSITION_INT', blocking=False)

        return {
            "latitude": positionStatus.lat,
            "longitude": positionStatus.lon,
            "altitude": positionStatus.alt,
            "heading": positionStatus.hdg
        }


    def isAutoEnabled(self):
        """
        Checks radio channel for whether autonomous mode is enabled by pilot

        Returns True/False
        """
        radioChannels = self.mavlinkConnection.recv_match(type='RC_CHANNELS_SCALED', blocking=False)
        channel_8 = int(radioChannels.chan8_scaled)

        return bool(channel_8)




    #TODO
    async def initWaypoints(self):
        pass

    #TODO
    async def autonTakeOff(self):
        await self.plane.action.arm()
        #Start multiprocessing for async telem updates during flight
        #Take off
        pass

    #TODO
    async def flyWaypoints(self):
        #have plane fly through waypoints
        pass

    #TODO
    async def autonLanding(self):

        #Land Plane
        self.stopTelemetryUpdates()
        await self.plane.action.disarm()
        pass


    #TODO
    def __repr__():
        return "UwU Statwus updwates"
