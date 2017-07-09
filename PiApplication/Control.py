"""
Bostin Technology  (see www.BostinTechnology.com)

For use with the CognIoT Sensors and uses the Android Application to read values

Command Line Options
    - Start Capturing Readings (default action)     -s --Start
    - Display Calibration                           -c --DisplayCal
    - Set Calibration                               -e --SetCal
    - Display Operational Parameters                -o --DisplayPara
    - Set Operational Parameters                    -a --SetPara
    - Reset                                         -t --Reset
    - Add New Sensor                                -n --NewSensor
    - Read Device ID                                -d --DeviceID
    - Read Sensor ID                                -i --SensorID
    - Set Logging Level                             -l --Logging

"""

import cls_DataAccessor
import cls_EEPROM
import Standard_Settings as SS
from cls_comms import i2c_comms
from cls_comms import SPi_comms
from cls_comms import Serial_comms
import dict_LoggingSetup

#import cls_SensorTemplate

###
### Need a bit of code that imports the correct iCog file.
### See importlib or search for dynamic import modules (dive into python)
###


from datetime import datetime
from datetime import timedelta

import time
import argparse
import sys
import logging
import logging.config
import importlib








def GetSerialNumber():
    """
    Get the System Serial number to be used as the Device ID
    returns the Serial Number or '0000000000000000'
    """
    try:
        log.debug("Opening proc/cpuinfo for CPU serial Number")
        f = open('/proc/cpuinfo')
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
        f.close
    except:
        cpuserial = '0000000000000000'
        log.error("Failed to open proc / cpuinfo, set to default")

    log.info("CPU Serial Number : %s" % cpuserial)
    return int(cpuserial, 16)

def GenerateTimeStamp():
    """
    Generate a timestamp in the correct format
    dd-mm-yyyy hh:mm:ss.sss
    datetime returns a object so it needs to be converted to a string and then redeuced to 23 characters to meet format
    """
    now = str(datetime.now())
    log.debug("Generated a timestamp %s" % now[:23])
    return now[:23]

def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """
    print("Current logging level is \n\n   DEBUG!!!!\n\n")
    
    global log
    # Create a logger with the name of the function
    logging.config.dictConfig(dict_LoggingSetup.log_cfg)
    log = logging.getLogger()


    #BUG: This is loading the wrong values into the log file
    log.info("File Logging Started, current level is %s" % log.getEffectiveLevel)
    log.info("Screen Logging Started, current level is %s" % log.getEffectiveLevel)
    
    return

################################################################################
# 
# The following functions are the client interaction functions
#
################################################################################

def SetandGetArguments():
    """
    Define the arguments available for the program and return any arguments set.

    """

    log.info("Setting and Getting Parser arguments")
    parser = argparse.ArgumentParser(description="Capture and send data for CognIoT sensors")
    parser.add_argument("-S", "--Start",
                    help="Start capturing data from the configured sensors and send them to the database")
    parser.add_argument("-t", "--Reset", 
                    help="Reset to the default values")
    parser.add_argument("-n", "--NewSensor", 
                    help="Add a new Sensor to this Raspberry Pi")
    parser.add_argument("-d", "--DeviceID", 
                    help="Display the Device ID for this Raspberry Pi")
    parser.add_argument("-i", "--SensorID", 
                    help="Display the Sensor IDs being used")
    parser.add_argument("-l", "--Logging", 
                    help="Set the logging level to be used (Default is OFF)")
    Cal_group = parser.add_mutually_exclusive_group()
    Cal_group.add_argument("-c", "--DisplayCal", 
                    help="Display the Calibration Data for the sensors")
    Cal_group.add_argument("-e", "--SetCal", 
                    help="Set new Calibration Data for the sensors")
    Para_group = parser.add_mutually_exclusive_group()
    Para_group.add_argument("-o", "--DisplayPara", 
                    help="Display the Operational parameters, e.g. Read Frequency")
    Para_group.add_argument("-a", "--SetPara", 
                    help="Set the Operational parameters, e.g. Read Frequency")

    log.debug("Parser values captured: %s" % parser.parse_args())
    return parser.parse_args()

def Start():
    """
    Perform the reading of and sending data to the AWS database
    This is the default action if no arguments are passed to the system.
    
    Order of the routine
    1. Access EEPROM to get sensor type
    2. Setup sensor
    3. Open data accessor link
    4. in loop
        read value
        post
    """

    # Load the data from the EEPROM on the ID-Iot chip
    i2c_connection = i2c_comms()
    eeprom_data = cls_EEPROM.ID_IoT(i2c_connection)

    # Load the correct sensor file
    icog_file = eeprom_data.ReturnSensorCommsFile()
    log.info("[CTRL] Loading the iCog Comms file:%s" % icog_file)

    try:
        # This doesn't initialise the iCog, just loads it
        #imported_icog = __import__(icog_file)
        imported_icog = importlib.import_module(icog_file)
    except:
        log.critical("[CTRL] Importing of the iCog file:%s failed, contact support" % icog_file)
        log.exception("[CTRL] Start Routine Exception Data")
        sys.exit()
    log.info("[CTRL] Importing of the iCog file:%s succeeded (%s)" % (icog_file,imported_icog))
    
    # Open the right bus connection to work with the icog connected
    reqd_bus = eeprom_data.ReturnBusType()
    if reqd_bus == SS.SPI:
        icog_connection = SPi_comms()
    elif reqd_bus == SS.SERIAL:
        icog_connection = Serial_Comms()
    elif reqd_bus == SS.I2C:
        icog_connection = i2c_connection
    else:
        log.critical("[CTRL] Required Connection bus:%s is not supported, contact Support" % reqd_bus)
        log.exception("[CTRL] Start Routine Exception Data")
        sys.exit()
    log.info("[CTRL] Required Connection bus:%s loaded" % icog_connection)
    
    # Retrieve Calibration Data and pass it to the iCog
    calib_data = eeprom_data.ReturnCalibrationData()
    
    log.debug("[CTRL] calibration data being passed into iCog:%s" % calib_data)
    # Initialise the iCog
    icog = imported_icog.iCog(icog_connection, calib_data)
    log.debug("[CTRL] imported icog:%s" % icog)
    
    # Sit in a loop reading the values back and writing them to the data connection
    # values available from the i_cog
    #   StartSensor, EndReadings, ReadValue, ReturnReadFrequency
    # put it all in a try loop to use CTRL-C to cancel
    print("Reading Values from sensor\n")
    print("CTRL-C to cancel")

    read_freq = icog.ReturnReadFrequency()
    log.debug("[CTRL] Read Frequency:%s" % read_freq)
    try:
        icog.StartSensor()
        while True:
            # Start the timer
            endtime = datetime.now() + timedelta(seconds=read_freq)
            print("\r\r\r\r\r\r\rReading", end="")

            #Read the value
            reading = icog.ReadValue()
            #TODO: Convert to a post
            log.info("[CTRL] Value Read back from the sensor:%s" % reading)

            # Wait for timeout
            waiting = False
            while endtime < datetime.now():
                if waiting == False:
                    print("\r\r\r\r\r\r\rWaiting", end="")
                    waiting=True
            
    except KeyboardInterrupt:
        # CTRL - C entered
        print(" CTRL-C entered")
    except:
        #Error occurrred
        log.critical("[CTRL] Error occurred whilst looping to read values")
        print("\nCRITICAL ERROR during rading of sensor values- contact Support\n")
        log.exception("[CTRL] Start reading loop Exception Data")

    
    
    #HERE!!
    

    


###
###
### The routine beneath here needs a complete review and refresh. All the names
### will have been changed and altered to suit the new structure
###
###

    # setup the connection to the AWS database
    dbconn = DataAccessor.DynamodbConnection()
    log.info("Connected to AWS database")
    log.debug("Database connection:%s" % dbconn)



    # main bit stolen from the Bananas code in threading
    if (time.time()- self.starttime) > self.sensor.readfrequency:
        self.log.debug("Thread Time to read values for thread:%s" % self.threadname)
        # Read the data (uuid, bustype, busnumber, deviceaddress)
        info = iCOGSensorComms.ReadData(self.sensor.uuid, self.sensor.bustype, self.sensor.busnumber, self.sensor.sensoraddress)
        self.log.debug("Thread %s: Read data from Sensor: %s" %( self.threadname, info))

        #Write the data from the sensor to the database
        DataAccessor.WriteValues(self.conn, info, GenerateTimeStamp(), self.sensor.uuid, self.sensor.sensor, self.sensor.sensoracroynm, self.sensor.sensordescription)
        self.log.debug("Thread %s has written data to AWS" % self.threadname)

        # Reset the timer
        self.starttime = time.time()
    #self.log.debug("Time elapsed during loop check:%f" %(starttime - time.time()))    
    
    return

def Reset():
    """
    Reset the program back to using the default values
    Clear any cached sensor data
    
    setup i2c comms
    provide menu to reset the Id-IoT
    using the iCog to get the data values.
    """
    print ("Not yet Implemented")
    return

def NewSensor():
    """
    Perform the necessary actions to add a new sensor to the system
    """
    print ("Not yet Implemented")
    return

def DisplayDeviceID():
    """
    Display the Device ID to the user
    """
    print ("Not yet Implemented")
    return

def DisplaySensorID():
    """
    Perform the necessary actions to display the Sensor ID being used
    """
    print ("Not yet Implemented")
    return
    
def DisplayCal():
    """
    Perform the necessary actions to display the Calibration data being used
    
    """
    print ("Not yet Implemented")
    return
    
def SetCal():
    """
    Perform the necessary actions to set the Calibration data being used
    
    """
    print ("Not yet Implemented")
    return
    
def DisplayParameters():
    """
    Perform the necessary actions to display the parameter data being used
    
    """
    print ("Not yet Implemented")
    return
    
def SetParameters():
    """
    Perform the necessary actions to allow the clinet to set the parameter data being used
    
    Parameters to be captured
    - Sensor Acroynm
    - Sensor Description
    - Read Frequency
    """
    print ("Not yet Implemented")
    return

def SetLogging():
    """
    Perform the necessary actions to achange the logging level being used

    The default logging level is zero
    """
    print ("Not yet Implemented")
    return
 
################################################################################
# 
# The following function is main - the entry point
#
################################################################################

def main():
    """
    This routine is the main called routine and therefore determines what action to take based on the arguments given.
    
    """
    
    SetupLogging()
    
    args = SetandGetArguments()
    
    # First print a 'splash screen'
    device_id = GetSerialNumber()
    print("Bostin Technology\n")
    print("\nDevice ID: %s" % device_id)
    print("\nTo Exit, CTRL-c\n\n")

### Add a proper splash screen

    
    #TODO: print out the values being used, especially if they are the defaults.
    
    #TODO: probably needs something to bomb out if there is a failure

    # Note: The default is Start, hence it is the else clause
    if args.Start: 
        Start()              #TODO: Complete routine
    elif args.Reset: 
        Reset()              #TODO: Not started
    elif args.NewSensor:
        NewSensor()          #TODO: Not started
    elif args.DeviceID:
        DisplayDeviceID()    #TODO: Not started
    elif args.SensorID:
        DisplaySensorID()    #TODO: Not started
    elif args.DisplayCal:
        DisplayCal()         #TODO: Not started
    elif args.SetCal:
        SelCal()             #TODO: Not started
    elif args.DisplayPara:
        DisplayParameters()  #TODO: Not started
    elif args.SetPara:
        SetParameters()      #TODO: Not started
    elif args.Logging:
        SetLogging()         #TODO: Not started
    else:
        Start()              

    
        

    
# Only call the Start routine if the module is being called directly, else it is handled by the calling program
if __name__ == "__main__":

    main()

