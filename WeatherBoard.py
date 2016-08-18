#!/usr/bin/env python
#
# Weather Board Test File
# Version 1.6 July 22, 2016
#
# SwitchDoc Labs
# www.switchdoc.com
#
#

# imports

import sys
import time
from datetime import datetime
import random 


import config

import subprocess
import CHIP_IO.GPIO as GPIO

sys.path.append('./RTC_SDL_DS3231')
sys.path.append('./SDL_Pi_WeatherRack')


import SDL_DS3231
import BMP280
import SDL_Pi_WeatherRack as SDL_Pi_WeatherRack


################
# Device Present State Variables
###############

as3935_Interrupt_Happened = False;

config.AS3935_Present = False
config.DS3231_Present = True 
config.BMP280_Present = False
config.FRAM_Present = False
config.HTU21DF_Present = False
config.AM2315_Present = False
config.ADS1015_Present = False
config.ADS1115_Present = False
config.OLED_Present = False


def returnStatusLine(device, state):

	returnString = device
	if (state == True):
		returnString = returnString + ":   \t\tPresent" 
	else:
		returnString = returnString + ":   \t\tNot Present"
	return returnString





###############   

#WeatherRack Weather Sensors
#
# GPIO Numbering Mode GPIO.BCM
#

anemometerPin = "XIO-P6"
rainPin = "XIO-P7"

# constants

SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1    # internally, the library checks for ADS1115 or ADS1015 if found

#sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
#Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

weatherStation = SDL_Pi_WeatherRack.SDL_Pi_WeatherRack(anemometerPin, rainPin, 0,0, SDL_MODE_I2C_ADS1015)

weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)
#weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)


################

# DS3231/AT24C32 Setup
filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.utcnow()

ds3231 = SDL_DS3231.SDL_DS3231(2, 0x68)


try:

	#comment out the next line after the clock has been initialized
	# ds3231.write_now()
	print "DS3231=\t\t%s" % ds3231.read_datetime()
	config.DS3231_Present = True
	print "----------------- "
	print "----------------- "
	print " AT24C32 EEPROM"
	print "----------------- "
	print "writing first 4 addresses with random data"
	for x in range(0,4):
		value = random.randint(0,255)
		print "address = %i writing value=%i" % (x, value) 	
		ds3231.write_AT24C32_byte(x, value)
	print "----------------- "
	
	print "reading first 4 addresses"
	for x in range(0,4):
		print "address = %i value = %i" %(x, ds3231.read_AT24C32_byte(x)) 
	print "----------------- "

except IOError as e:
	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.DS3231_Present = False
	# do the AT24C32 eeprom

	
################

# BMP280 Setup

try:
	bmp280 = BMP280.BMP280()
	config.BMP280_Present = True

except IOError as e:

	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.BMP280_Present = False

################

# HTU21DF Detection 
try:
	HTU21DFOut = subprocess.check_output(["htu21dflib/htu21dflib","-l"])
	config.HTU21DF_Present = True
except:
	config.HTU21DF_Present = False

# Main Loop - sleeps 10 seconds
# Tests all I2C and WeatherRack devices on Weather Board 


# Main Program

print ""
print "Weather Board Demo / Test Version 1.6 - SwitchDoc Labs"
print ""
print ""
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""

totalRain = 0


# print "----------------------"
# print returnStatusLine("DS3231",config.DS3231_Present)
# print returnStatusLine("BMP280",config.BMP280_Present)
# print returnStatusLine("FRAM",config.FRAM_Present)
# print returnStatusLine("HTU21DF",config.HTU21DF_Present)
# print returnStatusLine("AM2315",config.AM2315_Present)
# print returnStatusLine("ADS1015",config.ADS1015_Present)
# print returnStatusLine("ADS1115",config.ADS1115_Present)
# print returnStatusLine("AS3935",config.AS3935_Present)
# print returnStatusLine("OLED",config.OLED_Present)
# print returnStatusLine("SunAirPlus",config.SunAirPlus_Present)
# print "----------------------"







while True:


	print "----------------- "
	if (config.DS3231_Present == True):
		print " DS3231 Real Time Clock"
	else:
		print " DS3231 Real Time Clock Not Present"
	
	print "----------------- "
	#

	if (config.DS3231_Present == True):
		currenttime = datetime.utcnow()

		deltatime = currenttime - starttime
	 
		print "Chip  =\t\t" + time.strftime("%Y-%m-%d %H:%M:%S")

		if (config.OLED_Present):
			Scroll_SSD1306.addLineOLED(display,"%s" % ds3231.read_datetime())

		print "DS3231=\t\t%s" % ds3231.read_datetime()
	
		print "DS3231 Temperature= \t%0.2f C" % ds3231.getTemp()
		print "----------------- "



	print "----------------- "
	print " WeatherRack Weather Sensors" 
	print "----------------- "
	#

 	currentWindSpeed = weatherStation.current_wind_speed()/1.6
  	currentWindGust = weatherStation.get_wind_gust()/1.6
  	totalRain = totalRain + weatherStation.get_current_rain_total()/25.4
  	print("Rain Total=\t%0.2f in")%(totalRain)
  	print("Wind Speed=\t%0.2f MPH")%(currentWindSpeed)
	if (config.OLED_Present):
		Scroll_SSD1306.addLineOLED(display,  ("Wind Speed=\t%0.2f MPH")%(currentWindSpeed))
		Scroll_SSD1306.addLineOLED(display,  ("Rain Total=\t%0.2f in")%(totalRain))
  		if (config.ADS1015_Present or config.ADS1115_Present):	
			Scroll_SSD1306.addLineOLED(display,  "Wind Dir=%0.2f Degrees" % weatherStation.current_wind_direction())

    	print("MPH wind_gust=\t%0.2f MPH")%(currentWindGust)
  	if (config.ADS1015_Present or config.ADS1115_Present):	
		print "Wind Direction=\t\t\t %0.2f Degrees" % weatherStation.current_wind_direction()
		print "Wind Direction Voltage=\t\t %0.3f V" % weatherStation.current_wind_direction_voltage()

	print "----------------- "
	print "----------------- "
	if (config.BMP280_Present == True):
		print " BMP280 Barometer"
	else:
		print " BMP280 Barometer Not Present"
	print "----------------- "

	if (config.BMP280_Present):
		print 'Temperature = \t{0:0.2f} C'.format(bmp280.read_temperature())
		print 'Pressure = \t{0:0.2f} KPa'.format(bmp280.read_pressure()/1000)
		print 'Altitude = \t{0:0.2f} m'.format(bmp280.read_altitude())
		print 'Sealevel Pressure = \t{0:0.2f} KPa'.format(bmp280.read_sealevel_pressure()/1000)
		if (config.OLED_Present):
			Scroll_SSD1306.addLineOLED(display, 'Press= \t{0:0.2f} KPa'.format(bmp280.read_pressure()/1000))
			if (config.HTU21DF_Present == False):
				Scroll_SSD1306.addLineOLED(display, 'InTemp= \t{0:0.2f} C'.format(bmp280.read_temperature()))
	print "----------------- "

	print "----------------- "
	if (config.HTU21DF_Present == True):
		print " HTU21DF Temp/Hum"
	else:
		print " HTU21DF Temp/Hum Not Present"
	print "----------------- "

	# We use a C library for this device as it just doesn't play well with Python and smbus/I2C libraries
	if (config.HTU21DF_Present):
		HTU21DFOut = subprocess.check_output(["htu21dflib/htu21dflib","-l"])
		splitstring = HTU21DFOut.split()

		HTUtemperature = float(splitstring[0])	
		HTUhumidity = float(splitstring[1])	
		print "Temperature = \t%0.2f C" % HTUtemperature
		print "Humidity = \t%0.2f %%" % HTUhumidity
		if (config.OLED_Present):
			Scroll_SSD1306.addLineOLED(display,  "InTemp = \t%0.2f C" % HTUtemperature)
	print "----------------- "

	print "Sleeping 10 seconds"
	time.sleep(10.0)


