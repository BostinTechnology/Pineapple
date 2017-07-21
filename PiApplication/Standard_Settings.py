#Bus types
I2C = "I2C"
SPI = "SPI"
SERIAL = "Serial"

DATAFILE_NAME = "datafile.txt"
DATAFILE_LOCATION = "." #"CognIoT"

CUSTFILE_NAME = "custfile.txt"
CUSTFILE_LOCATION = "."


MIN_DISK_SPACE = 50 * 1024             # Minimum disk space required at startup (measured in bytes)

#EEPROM Settings
CALIB_PAGE_LENGTH = 16            # The number of bytes in the 'row' of calibration data

RECORDFILE_LOCATION = "."
RECORDFILE_NAME = "records.txt"
RECORD_TRY_COUNT = 10               # How many times, when connected the Data Accessor will try and send a record

#Database Locations
DB_LOCAL = 'Local'
DB_AWS = 'AWS'

#Database Structure Values
MAX_ACROYNM_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 100

def test():
    
    return
    
