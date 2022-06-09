import time
import serial
from pymavlink import mavutil
 
import asyncio
from mavsdk import System
 
portName = "/dev/ttyTHS0"
baudrt = 57600
 
UART_port = serial.Serial(
	port = portName,
	baudrate=baudrt
)
time.sleep(1)
 
#ports = serial.tools.list_ports.comports()
 
#connection = mavutil.mavlink_connection(portName, baud=baudrt)
time.sleep(1)
 
 
async def run():
 
	drone = System()
	print("works1")
	await drone.connect(system_address="serial:///dev/ttyTHS0:57600")
	print("works2")
 	
	async for position in drone.telemetry.position():
        	print(position)
 
	await drone.action.arm()
 
 
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
print("works")
 

