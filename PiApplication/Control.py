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

from cls_DataAccessor import DataAccessor
import cls_EEPROM
import Standard_Settings as SS
from cls_comms import i2c_comms
from cls_comms import SPi_comms
from cls_comms import Serial_comms
import dict_LoggingSetup

#import cls_SensorTemplate
# The required iCog is imported in the code once it has been determined

from datetime import datetime
from datetime import timedelta

import time
import argparse
import sys
import logging
import logging.config
import importlib
import inspect


# The following global variables are used.
gbl_log = ""




def GetSerialNumber():
    """
    Get the System Serial number to be used as the Device ID
    returns the Serial Number or '0000000000000000'
    """
    try:
        gbl_log.debug("[CTRL] Opening proc/cpuinfo for CPU serial Number")
        f = open('/proc/cpuinfo')
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
        f.close
    except:
        cpuserial = '0000000000000000'
        gbl_log.error("[CTRL] Failed to open proc / cpuinfo, set to default")

    gbl_log.info("[CTRL] CPU Serial Number : %s" % cpuserial)
    return int(cpuserial, 16)

def GenerateTimeStamp():
    """
    Generate a timestamp in the correct format
    dd-mm-yyyy hh:mm:ss.sss
    datetime returns a object so it needs to be converted to a string and then redeuced to 23 characters to meet format
    """
    now = str(datetime.now())
    gbl_log.debug("[CTRL] Generated a timestamp %s" % now[:23])
    return now[:23]

def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """
    print("Current logging level is \n\n   DEBUG!!!!\n\n")
    
    global gbl_log
    # Create a logger with the name of the function
    logging.config.dictConfig(dict_LoggingSetup.log_cfg)
    gbl_log = logging.getLogger()


    #BUG: This is loading the wrong values into the log file
    gbl_log.info("[CTRL] File Logging Started, current level is %s" % gbl_log.getEffectiveLevel)
    gbl_log.info("[CTRL] Screen Logging Started, current level is %s" % gbl_log.getEffectiveLevel)
    
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

#BUG: The way the arguments is required is not as expected
# Had to type sudo python3 Control.py -c DISPLAYCAL
# to get it to work
    gbl_log.info("[CTRL] Setting and Getting Parser arguments")
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
                    help="Display the Calibration Data for the sensors, e.g. Read Frequency")
    Cal_group.add_argument("-e", "--SetCal", 
                    help="Set new Calibration Data for the sensors, e.g. Read Frequency")
    Para_group = parser.add_mutually_exclusive_group()
    Para_group.add_argument("-o", "--DisplayCustInfo", 
                    help="Display the Customer Information, e.g. Customer Name")
    Para_group.add_argument("-a", "--SetCustInfo", 
                    help="Set the Operational parameters, e.g. Customer Name")

    gbl_log.debug("[CTRL] Parser values captured: %s" % parser.parse_args())
    return parser.parse_args()

def SetupSensor():
    """
    This function performs the following
    - Connect to the ID_IoT chip and retive all the infromation
    - load the correct icog file
    - Transfer the configuration information into the loaded icog
    - set the global variable icog to the required icog
    returns the instance of the icog and the eeprom
    """
  
    # Load the data from the EEPROM on the ID-Iot chip
    i2c_connection = i2c_comms()
    eeprom = cls_EEPROM.ID_IoT(i2c_connection)

    # Load the correct sensor file
    icog_file = eeprom.ReturnSensorCommsFile()
    gbl_log.info("[CTRL] Loading the iCog Comms file:%s" % icog_file)

    try:
        # This doesn't initialise the iCog, just loads it
        #imported_icog = __import__(icog_file)
        imported_icog = importlib.import_module(icog_file)
    except:
        gbl_log.critical("[CTRL] Importing of the iCog file:%s failed, contact support" % icog_file)
        gbl_log.exception("[CTRL] Start Routine Exception Data")
        sys.exit()
    gbl_log.info("[CTRL] Importing of the iCog file:%s succeeded (%s)" % (icog_file,imported_icog))
    
    # Open the right bus connection to work with the icog connected
    reqd_bus = eeprom.ReturnBusType()
    if reqd_bus == SS.SPI:
        icog_connection = SPi_comms()
    elif reqd_bus == SS.SERIAL:
        icog_connection = Serial_Comms()
    elif reqd_bus == SS.I2C:
        icog_connection = i2c_connection
    else:
        gbl_log.critical("[CTRL] Required Connection bus:%s is not supported, contact Support" % reqd_bus)
        gbl_log.exception("[CTRL] Start Routine Exception Data")
        sys.exit()
    gbl_log.info("[CTRL] Required Connection bus:%s loaded" % icog_connection)
    
    # Retrieve Calibration Data and pass it to the iCog
    calib_data = eeprom.ReturnCalibrationData()
    
    gbl_log.debug("[CTRL] calibration data being passed into iCog:%s" % calib_data)
    # Initialise the iCog
    icog = imported_icog.iCog(icog_connection, calib_data)
    gbl_log.debug("[CTRL] imported icog:%s" % icog)

    return (icog, eeprom)
    
def Start(cust_info):
    """
    Perform the reading of and sending data to the AWS database
    This is the default action if no arguments are passed to the system.
    
    Order of the routine


    3. Open data accessor link
    4. in loop
        read value
        post
    """
 
    (icog, eeprom) = SetupSensor()
    
    # Sit in a loop reading the values back and writing them to the data connection
    # values available from the i_cog
    #   StartSensor, EndReadings, ReadValue, ReturnReadFrequency
    # put it all in a try loop to use CTRL-C to cancel
    print("Reading Values from sensor\n")
    print("CTRL-C to cancel")

    DataAcc = DataAccessor(cust_info["device"], cust_info["sensor"], cust_info["acroynm"], cust_info["description"])
    read_freq = icog.ReturnReadFrequency()
    #read_freq = 10
    gbl_log.debug("[CTRL] Read Frequency:%s" % read_freq)
    try:
        icog.StartSensor()
        while True:
            # Start the timer
            endtime = datetime.now() + timedelta(seconds=read_freq)
            print("\r\r\r\r\r\r\rReading", end="")

            #Read the value
            reading = icog.ReadValue()

            gbl_log.info("[CTRL] Value Read back from the sensor:%s" % reading)
            
            DataAcc.DataIn(reading)
            # The following but needs to be put into a thread for parallel running
            DataAcc.TransmitData()

            # Wait for timeout
            waiting = False
            while endtime > datetime.now():
                if waiting == False:
                    print("\r\r\r\r\r\r\rWaiting(last reading:%s)" % reading, end="")
                    gbl_log.debug("[CTRL] Waiting for timeout to complete")
                    waiting=True
            
    except KeyboardInterrupt:
        # CTRL - C entered
        print(" CTRL-C entered")
    except:
        #Error occurrred
        gbl_log.critical("[CTRL] Error occurred whilst looping to read values")
        print("\nCRITICAL ERROR during rading of sensor values- contact Support\n")
        gbl_log.exception("[CTRL] Start reading loop Exception Data")

    return

def Reset():
    """
    Reset the program back to using the default values
    Clear any cached sensor data
    
    setup i2c comms
    provide menu to reset the Id-IoT
    using the iCog to reset the config and get the data values.
    reset all the configuration data back to original
    """
    check = input("Are you sure you want to reset back to default values (y/n)?")
    if check.upper() == "Y":
        (icog, eeprom) = SetupSensor()
        calib = icog.ResetCalibration()
        eeprom.ResetCalibrationData(calib)

        print("Calibration Data reset to default values")
    
    print("Clearing of User data not yet implemented")
    
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
    #BUG: calib_data is not set as the icog is not instantiated unless Start called
    # Need to add a check to see if Setup has alread been run and therefore doesn't need to be rerun
    # Put this check in SetupSensor()
    
    (icog, eeprom) = SetupSensor()
    calib_data = icog.ReturnCalibrationData()
    print("Setting                  Value")
    print("==============================")
    for item in calib_data:
        print("%s%s" %( '{0: <25}'.format(item), calib_data[item]))

    return
    
def SetCal():
    """
    Perform the necessary actions to set the Calibration data being used
    Call the icog SetCalibration routine which returns the calibration data
    Write the calibration data to the ID_IoT
    """
    gbl_log.info("[CTRL] Setting the Calibration")
    (icog, eeprom) = SetupSensor()
    calib = icog.SetCalibration()
    if len(calib) > 1:
        # data returned, so nothing to write
        eeprom.ResetCalibrationData(calib)

        print("Calibration Data Set")
        gbl_log.info("[CTRL] Calibration data set")
    else:
        print("No change to the calibration data")
        gbl_log.info("[CTRL] No change to the Calibration")
    
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
    - local or remote database
    """
    print ("Not yet Implemented")
    return

def SetLogging():
    """
    Perform the necessary actions to change the logging level being used

    The default logging level is zero
    """
    print ("Not yet Implemented")
    return

def SplashScreen():
    print("***********************************************")
    print("*             Bostin Technology               *")
    print("*                                             *")
    print("*             Mobile IoT Sensor               *")
    print("*                                             *")
    print("*        for more info www.cognIoT.eu         *")
    print("***********************************************\n")
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
    
    SplashScreen()
    
    SetupLogging()
    
    args = SetandGetArguments()
    
    # First print a 'splash screen'
    device_id = GetSerialNumber()
    print("Bostin Technology\n")
    print("\nDevice ID: %s" % device_id)
    print("\nTo Exit, CTRL-c\n\n")

    customer_info = {"device" : 1, "sensor" : 1, "acroynm" : "LghtSns1", "description" : "Light Sensor in the Office"}
    
    #TODO: print out the values being used, especially if they are the defaults.
    
    #TODO: probably needs something to bomb out if there is a failure
    
    #TODO: Need to add some disk management, a generic check for overall disk space.
        # See one of my photography apps
        
    
    # Note: The default is Start, hence it is the else clause
    if args.Start: 
        Start(customer_info)
    elif args.Reset: 
        Reset()
    elif args.NewSensor:
        NewSensor()          #TODO: Not started
    elif args.DeviceID:
        DisplayDeviceID()    #TODO: Not started
    elif args.SensorID:
        DisplaySensorID()    #TODO: Not started
    elif args.DisplayCal:
        DisplayCal()
    elif args.SetCal:
        SetCal()
        DisplayCal()
    elif args.DisplayCustInfo:
        DisplayParameters()  #TODO: Not started
    elif args.SetCustInfo:
        SetParameters()      #TODO: Not started
    elif args.Logging:
        SetLogging()         #TODO: Not started
    else:
        Start(customer_info)              

    
        

    
# Only call the Start routine if the module is being called directly, else it is handled by the calling program
if __name__ == "__main__":

    main()

