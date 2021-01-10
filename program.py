import csv
import os
import ephem
from sense_hat import SenseHat
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from picamera import PiCamera

### Create instances
sensei = SenseHat()
cam = PiCamera()

# test skála

### Define variables
path = Path(__file__).parent.resolve()
dataFile = path/'data.csv'

startTime = datetime.now()
nowTime = datetime.now()

cam.resolution = (1296,972)
imgCounter = 0

name = "ISS (ZARYA)"
line1 = "1 25544U 98067A   20316.41516162  .00001589  00000+0  36499-4 0  9995"
line2 = "2 25544  51.6454 339.9628 0001882  94.8340 265.2864 15.49409479254842"
iss = ephem.readtle(name, line1, line2) # ISS instance

### Create the CSV data file
with open(dataFile, 'w') as f:
    writer = csv.writer(f)
    header = ("dateTime", "temp", "hum", "press")
    writer.writerow(header)

### Functions for the main loop

def writeData(file, data):
    with open(file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def convert(angle):

    # Convert an ephem angle (degrees:minutes:seconds) to
    # an EXIF-appropriate representation (rationals)
    # e.g. '51:35:19.7' to '51/1,35/1,197/10'
    # Return a tuple containing a boolean and the converted angle,
    # with the boolean indicating if the angle is negative.

    degrees, minutes, seconds = (float(field) for field in str(angle).split(":"))
    exif_angle = f'{abs(degrees):.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return degrees < 0, exif_angle

"""
def capture(camera, image):
    # Use `camera` to capture an `image` file with lat/long EXIF data.
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
"""

### Main loop

while (nowTime < startTime + timedelta(seconds = 10)):
    # Harvest data
    writeData(dataFile, (datetime.now(), sensei.temperature, sensei.humidity, sensei.pressure))

    iss.compute() # Get the lat/long values from ephem

    # convert the latitude and longitude to EXIF-appropriate representations
    south, exif_latitude = convert(iss.sublat)
    west, exif_longitude = convert(iss.sublong)

    # set the EXIF tags specifying the current location
    cam.exif_tags['GPS.GPSLatitude'] = exif_latitude
    cam.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    cam.exif_tags['GPS.GPSLongitude'] = exif_longitude
    cam.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

    # Take photo
    cam.capture("image" + str(imgCounter) + ".jpg")

    imgCounter += 1
    nowTime = datetime.now()

"""
camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture("image.jpg")
"""