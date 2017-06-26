"""
This program programs the ID-IoT chip with default settings.


TODO: Complete debugging as it is currently not writing values.
got this in the log file
25-06-2017 22:33:16 - DEBUG    - [ID_IoT] Connection Data to be written:[1, 68, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 255, 255]
25-06-2017 22:33:16 - INFO     - [EEPROM] Set Device Connectivity with dataset:[1, 68, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 255, 255]
25-06-2017 22:33:16 - DEBUG    - [EEPROM] Set Device Connectivity response status (1=True):False
25-06-2017 22:33:16 - DEBUG    - [ID_IoT] Write Map Version to be written:[0, 2]
25-06-2017 22:33:16 - WARNING  - [COMMS] Unable to write byte:0 of value:0 from i2c device:80 and got this response:unknown
25-06-2017 22:33:16 - DEBUG    - [EEPROM] Set Map Version response status (1=True):False

when writing data, there is no response except an exception.


2 Falses!
"""

import cls_EEPROM
import Standard_Settings as SS
from cls_comms import i2c_comms
import logging
import logging.config


ID_IoT_map =   [['i_cog_Ps_1','i-cog.Ps.1','Pressure / Altitude','ST LPS25HB',0x01,0x01,[0x01,0xff,0x00,0x00,0x00,0x01,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ps_2','i-cog.Ps.2','Pressure / Altitude','Bosch',0x01,0x02,[0x01,0xff,0x00,0x00,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ps_3','i-cog.Ps.3','Pressure / Altitude','Freescale',0x01,0x03,[0x01,0xff,0x00,0x00,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ls_1','i-cog.Ls.1','Light','Intersil',0x02,0x01,[0x01,0x44,0x00,0x00,0x00,0x02,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ls_2','i-cog.Ls.2','Light','Vishay UV',0x02,0x02,[0x01,0xff,0x00,0x00,0x00,0x02,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ls_3','i-cog.Ls.3','Light','Vishay VCNL4040',0x02,0x03,[0x01,0xff,0x00,0x00,0x00,0x02,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ts_1','i-cog.Ts.1','Temperature','ST HTS221',0x03,0x01,[0x01,0x5f,0x00,0x00,0x00,0x03,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ts_2','i-cog.Ts.2','Temperature','Measurement Specialities',0x03,0x02,[0x01,0xff,0x00,0x00,0x00,0x03,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Ts_3','i-cog.Ts.3','Temperature','TI HDC1008',0x03,0x03,[0x01,0xff,0x00,0x00,0x00,0x03,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Rs_1','i-cog.Rs.1','Rate Sensor','Bosch,0x04',0x01,[0x01,0xff,0x00,0x00,0x00,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Rs_2','i-cog.Rs.2','Rate Sensor','Freescale MMA8652FC',0x04,0x02,[0x01,0x1d,0x00,0x00,0x00,0x04,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Rs_3','i-cog.Rs.3','Rate Sensor','ST LIS3DH',0x04,0x03,[0x01,0xff,0x00,0x00,0x00,0x04,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Rs_4','i-cog.Rs.4','Rate Sensor','Freescale FXAS21002C',0x04,0x04,[0x01,0xff,0x00,0x00,0x00,0x04,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]],
                ['i_cog_Rs_5','i-cog.Rs.5','Rate Sensor','Freescale FXOS8700CQ',0x04,0x05,[0x01,0xff,0x00,0x00,0x00,0x04,0x05,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF]]
                ]

ID_IoT_map_version = [0x00, 0x02]


LOG_CFG = dict(
    version = 1,
    formatters = {
        'full': {'format':
              '%(asctime)s - %(levelname)-8s - %(message)s',
              'datefmt': '%d-%m-%Y %H:%M:%S'},
        },
    handlers = {              
        'file': {'class': 'logging.FileHandler',
                'formatter': 'full',
                'level': logging.DEBUG,
                'filename': 'ID_IoTReset.log',
                'mode': 'w'},
                  
        },
    root = {
        'handlers': ['file'],
        'level': logging.DEBUG,
        },
        )



def choose_chip():
    """
    Using the ID_IoT map, provide a menu for the user to choose which chip
    """
    choice = -1
    confirm = ""
    print("Re-programming menu\n")
    print("Please choose iCog")
    while confirm.upper() != "Y":
        count = 0
        for i in ID_IoT_map:
            count = count + 1
            print ("%s - %s" %(count,i[1]))
        choice = input("Enter value between 1 - %s: " % count)
        if choice.isdigit() == False:
            print("Enter a number please")
            choice = -1
        elif int(choice) > count or int(count) < 1:
            print("Only numbers in the range 1 to %s are allowed\n%s" % count)
            choice = -1
        
        choice = int(choice) -1         # Convert the respnse to a number and reduce it by 1 to make it array value
        if choice > -1:
            print("Chosen device:%s" % ID_IoT_map[choice][1])
            confirm = input("Are you sure (y/n)? ")
            if confirm.upper() == "Y":
                log.debug("[ID_IoT] User has confirmed %s is the correct chip" % ID_IoT_map[choice][1])
            else:
                choice = -1
         # 
    return choice

def write_connection_data(eeprom,chosen):
    """
    Write the data for the selected chip
    """
    record = ID_IoT_map[chosen][6]
    log.debug("[ID_IoT] Connection Data to be written:%s" % record)
    response = eeprom.SetDeviceConnectivityData(record)
    return

def write_map_version(eeprom):
    """
    Write the map version
    """
    log.debug("[ID_IoT] Write Map Version to be written:%s" % ID_IoT_map_version)
    response = eeprom.SetMapVersion(ID_IoT_map_version)
    return    
    
def main():
    """
    This routine controls the programming of the iCof ID-IoT EEPROM utilising the functions that already exist
    in the 2 classes associated with the project
    Key Steps
        - Menu to choose the sensor to use
        - Reprogram the chip
        - Write a map version
        - re-generate the checksum
    
    """

    global log
    # Create a logger with the name of the function
    logging.config.dictConfig(LOG_CFG)
    log = logging.getLogger()
    log.info("[ID_IoT] Logging started")
    
    # Load the data from the EEPROM on the ID-Iot chip
    i2c_connection = i2c_comms()
    eeprom_data = cls_EEPROM.ID_IoT(i2c_connection, read_chip=False)
    
    selected = choose_chip()            # returns the record number

    write_connection_data(eeprom_data, selected)
    
    write_map_version(eeprom_data)
    
    return 

if __name__ == '__main__':
    main()

