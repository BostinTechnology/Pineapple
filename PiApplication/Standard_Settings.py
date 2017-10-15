#Bus types
I2C = "I2C"
SPI = "SPI"
SERIAL = "Serial"

# Datafile and Customer file locations
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
EEPROM_READ_RETRY = 5               # How many times it will try and read data from the EEPROM

#Database Locations
DB_LOCAL = 'DBLocal'
DB_AWS = 'AWS'
DB_REMOTE = 'Remote'

# Database API address information
DB_LOCAL_ADDR = 'localhost'
DB_LOCAL_PORT = '8080'
DB_AWS_ADDR = '192.168.1.182'
DB_AWS_PORT = '8080'
DB_REMOTE_PORT = '8080'         # Default Value

#Database Structure Values
MAX_ACROYNM_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 100

def test():

    return

