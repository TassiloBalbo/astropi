import csv
import os
import ephem
from sense_hat import SenseHat
from datetime import datetime, timedelta
from pathlib import Path
from picamera import PiCamera
from logzero import logger, logfile
from time import sleep

### Create instances -----------------------------------------------
sensei = SenseHat()
cam = PiCamera()


### Define variables -----------------------------------------------
path = Path(__file__).parent.resolve()
dataFile = path/"stratopi.csv"
logfile(path/"stratopi.log")

startTime = datetime.now()
nowTime = datetime.now()

cam.resolution = (1296,972)
imgCounter = 0 # used for numbering images

name = "ISS (ZARYA)"
line1 = "1 25544U 98067A   21050.35666428  .00001943  00000-0  43448-4 0  9992"
line2 = "2 25544  51.6441 205.5251 0003032  33.1814  49.2099 15.48980511270331"
iss = ephem.readtle(name, line1, line2)


### Create the CSV data file ---------------------------------------
with open(dataFile, 'w') as f:
	writer = csv.writer(f)
	header = ("dateTime", "temp", "hum", "press")
	writer.writerow(header)


### Functions for the main loop ------------------------------------

# write data to a csv file
def writeData(file, data):
	with open(file, 'a') as f:
		writer = csv.writer(f)
		writer.writerow(data)

# convert ephem coordinates to EXIF compatible coordinates
def convert(angle):

	degrees, minutes, seconds = (float(field) for field in str(angle).split(":"))
	exif_angle = f'{abs(degrees):.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
	return degrees < 0, exif_angle

# capture image with lat/long EXIF data
def capture(camera, image):
	iss.compute() # Get the lat/long values from ephem

	# convert the latitude and longitude to EXIF-appropriate representations
	south, exif_latitude = convert(iss.sublat)
	west, exif_longitude = convert(iss.sublong)

	# set the EXIF tags specifying the current location
	cam.exif_tags['GPS.GPSLatitude'] = exif_latitude
	cam.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
	cam.exif_tags['GPS.GPSLongitude'] = exif_longitude
	cam.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

	# capture the image
	cam.capture(image)

# Calculate data used
def calcData():
	dataUsed = 0
	for file in os.scandir(path):
		if not file.path.endswith(".py"):
			fileStats = os.stat(file)
			dataUsed += fileStats.st_size
	return round(dataUsed / (1024 * 1024), 2)

### Main loop ------------------------------------------------------

while (nowTime < startTime + timedelta(seconds = 10790)):
	logger.info(f"✅🚀 Loop #" + str(imgCounter) + " started")

	# Harvest and write data
	try:
		writeData(dataFile, (datetime.now(), round(sensei.temperature, 4), round(sensei.humidity, 4), round(sensei.pressure, 4)))
		logger.info(f"✅📜 Data recorded")
	except Exception as e:
		logger.error(f"❌📜 Failed to record data: {e.__class__.__name__}: {e}")

	# take a picture
	try:
		if imgCounter < 10:
			imgFile = "image000" + str(imgCounter) + ".jpg"
		elif imgCounter < 100:
			imgFile = "image00" + str(imgCounter) + ".jpg"
		elif imgCounter < 1000:
			imgFile = "image0" + str(imgCounter) + ".jpg"
		else:
			imgFile = "image" + str(imgCounter) + ".jpg"
		capture(cam, imgFile)
		logger.info(f"✅📸 Captured image " + imgFile)
	except Exception as e:
		logger.error(f"❌📸 Failed to capture image " + imgFile + " {e.__class__.__name__}: {e}")

	logger.info(f"✅🚀 Loop #" + str(imgCounter) + " ended")
	imgCounter += 1
	sleep(4)
	nowTime = datetime.now()

logger.info(f"✅ Experiment finished. 📷 Recorded " + str(imgCounter) + " images. 📦 Used " + str(calcData()) + "MB of data. ✅")