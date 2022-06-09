import time
import serial
import requests
from pymavlink import mavutil

import asyncio
import mavsdk
import plane

import json


# connection = mavutil.mavlink_connection(portName, baud=baudrt)
# time.sleep(1)


def setServerInfo():
    interopIP_Address = username = password = None

    choice = "n"
    while choice == "n":
        interopIP_Address = input("IP Address: ")
        print("Is [", interopIP_Address, "] correct? (y/n)")
        choice = input()

    choice = "n"
    while choice == "n":
        username = input("Username: ")
        print("Is [", username, "] correct? (y/n)")
        choice = input()

    choice = "n"
    while choice == "n":
        password = input("Password: ")
        print("Is [", password, "] correct? (y/n)")
        choice = input()

    return interopIP_Address, username, password


# this function should make a request to the ground station for input
# the infoFile param is for possible implementation of an auto-startup upon disconnect

def interopConnect(interopIP_Address, username, password):
    loginURL = "http://" + str(interopIP_Address) + "/api/login"
    logincreds = {'username': str(username), 'password': str(password)}

    try:
        loginRequest = requests.post(url=loginURL, json=logincreds)
        time.sleep(1)
        # arbitrary wait time for server request

        if ("200" in loginRequest.text):
            # upon successful request
            loginCookie = loginRequest.cookies
            return loginCookie
    except:
        print("Unable to connect")
        return None



# should raise an exception for login request not managed

def getMission(interopIP_Address, missionID, loginCookie):
    missionURL = "http://" + str(interopIP_Address) + "/api/missions/" + str(missionID)

    try:
        missionRequest = requests.get(url=missionURL, cookies=loginCookie)
        time.sleep(1)
        # arbitrary wait time for server request

        if ("200" in missionRequest.text):
            # upon successful request
            missionJSON = json.loads(missionRequest)
            return missionJSON
    except:
        print("Unable to connect")
        return None


# should raise an exception for login request not managed

#connect to interop server
interopLoginInfo = setServerInfo()
loginCookie = interopConnect(*interopLoginInfo)
mission = None

if loginCookie != None:
    missionID = input("Mission ID: ")
    mission = getMission(interopLoginInfo[0], missionID, loginCookie)
else:
    print("T^T")


def main():
    # connect to interop server
    portName = "/dev/ttyTHS0"
    baudrt = 57600

    UART_port = serial.Serial(
        port=portName,
        baudrate=baudrt
    )
    time.sleep(1)
    # connection = mavutil.mavlink_connection(portName, baud=baudrt)
    # time.sleep(1)

    interopLoginInfo = setServerInfo()
    loginCookie = interopConnect(*interopLoginInfo)
    mission = None

    if loginCookie != None:
        missionID = input("Mission ID: ")
        mission = getMission(interopLoginInfo[0], missionID, loginCookie)
    else:
        print("T^T")

    #connect to plane
    UAV = plane.Plane("serial:///dev/ttyTHS0:57600", mission) #No current error handling for unrecieved mission

    """
    Stuff for plane to do
    """
