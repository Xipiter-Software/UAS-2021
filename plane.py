import time
import serial
from pymavlink import mavutil

import asyncio
import mavsdk
from mavsdk.geofence import Point, Polygon

import requests
import math


class Plane:
    def __init__(self, system_address, missionDict):

        #open jetson serial port & init mavlink connection
        portName = "/dev/ttyTHS0"
        baudrate = 57600
        self.openSerialPort(portName, baudrate)

        self.mavlinkConnection = mavutil.mavlink_connection(portName, baud=baudrate)
        time.sleep(1)

        #initialize & connect to mavsdk object / plane
        self.plane = mavsdk.System()
        asyncio.run(self.connectPlane(system_address))

        #store mission dictionary
        self.missionDict = missionDict

        #set up mavsdk obstacle geofences & mavsdk mission
        asyncio.run(self.initFlightBounds())
        asyncio.run(self.intObstacles())
        asyncio.run(self.initWaypoints()) #TODO

        self.continousTelemUpdates = True

    #class constructor cannot be asynchronous
    async def connectPlane(self, system_address):
        await self.plane.connect(system_address=system_address)

    def openSerialPort(self, portName, baudrate):
        self.UART_port = serial.Serial(
            port=portName,
            baudrate=baudrate
        )
        time.sleep(1)

    def closeSerialPort(self):
        self.UART_port.close()

    async def initFlightBounds(self):
        flyZone = self.missionDict["flyZones"]
        self.maxAlt = flyZone["altitudeMax"]
        self.minAlt = flyZone["altitudeMin"]

        bounds = flyZone["boundaryPoints"]

        boundPoints = list()
        for point in bounds:
            lat, lon = point.items()
            boundPoints.append(
                Point(lat, lon)
            )

        boundary = Polygon(boundPoints, Polygon.FenceType.INCLUSION)
        await self.plane.geofence.upload_geofence([boundary])
        #use function return for geofence validation & error handling

    async def intObstacles(self):
        stationaryObstacles = self.missionDict["stationaryObstacles"]

        obstaclePolygons = list()
        for obstacle in stationaryObstacles:
            lat, lon, rad, height = obstacle.items()
            #mavsdk doesn't seem to have conditional geofences for obstacle height consideration

            obstaclePolygons.append(
                Polygon(self.obstaclePolygon(lat, lon, rad), Polygon.FenceType.EXCLUSION)
            )

        await self.plane.geofence.upload_geofence(obstaclePolygons)
        # use function return for geofence validation & error handling

    #returns a bounding box around the circlular obstacles
    def obstaclePolygon(self, lat, lon, distance):

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

    def startTelemetryUpdates(self, interopIP, loginCookie):

        telemPostURL = "http://" + str(interopIP) + "/api/telemetry"
        self.continousTelemUpdates = True

        while self.continousTelemUpdates:
            positionStatus = self.mavlinkConnection.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
            latitude = positionStatus.lat
            longitude = positionStatus.lon
            altitude = positionStatus.alt
            heading = positionStatus.hdg

            telem = {
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "heading": heading
            }

            requests.post(url=telemPostURL, json=telem, cookies=loginCookie)
            time.sleep(0.5)
            #2 Hz frequency - post request latency

    def stopTelemetryUpdates(self):
        self.continousTelemUpdates = False

    def isAutoEnabled(self):
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
