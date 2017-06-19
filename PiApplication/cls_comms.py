#!/usr/bin/env python3
"""
cls_comms
performs all the low level comms required for the various devices.

Requires sudo apt-get install python3-smbus

"""
#Bus types
I2C = "I2C"
SPI = "SPI"
SERIAL = "Serial"

import smbus
import serial
import sys


class Comms():
    """
    This routine will setup and control the low level comms out to the various
    protocols
    
    By default, it just creates an instance of itself and opens the port
    
    It is required to be given the port to work with, I2C, SPI, SERIAL
    - port is the type of connection I2C, SPI or SERIAL
    - address is the address of the device, default to 0x00 if not required
    """
    
    def __init__(self, port, address=b'\x00'):
        """
        Setup ready for comms, opening the requried port
        """
        self.sensor_address = address
        self._open_port()

            
        return
    
    def transcieve_data(self, data):
        """
        Send and receive data
        """
        
        return

    def send_data(self, data):
        """
        Send data on the chosen connection
        """
        return
        
    def read_data_byte(self, byte_addr):
        """
        Read a data byte on the chosen connection
        """
        self.read_address = address
        self.byte_addr = byte_addr
        self._i2c_read_byte()
        return

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------
        
    def _open_port(self):
        """
        Open the i2c comms port
        """
        try:
            self.connection = smbus.SMBus(1)
        except:# FileNotFoundError:
            log.critical("[COMMS] Unable to open comms port using smbus (_i2c_port), program halted")
            log.warning("Exception:%s" % traceback.format_exc())
            print("\nError Occurred, program halted - contact support\n")
            sys.exit()
 
        return
    
    def _read_byte(self):
        """
        Read a byte from the given address
        """
        try:
            value = self.connection.read_byte_data(self.sensor_address, self.byte_addr)
        except:
            log.warning("[COMMS] Unble to read byte:%s from i2c device:%s and got this response:%s"
                %(self.byte_addr, self.sensor_address, value)
        return value
    
    def _write_byte(self)
        """
        Write a byte from the given address
        """
        try:
            respone = self.connection.write_byte_data(self.sensor_address, self.byte_addr, self.value)
        except:
            log.warning("[COMMS] Unble to write byte:%s of value:%s from i2c device:%s and got this response:%s"
                %(self.byte_addr, self.value, self.sensor_address, response)
        return response    


class SPi_Comms():
    """
    This routine will setup and control the low level comms out to the various
    protocols
    
    By default, it just creates an instance of itself and opens the port
    
    It is required to be given the port to work with, I2C, SPI, SERIAL
    - port is the type of connection I2C, SPI or SERIAL
    - address is the address of the device, default to 0x00 if not required
    """
    
    def __init__(self, address=b'\x00'):
        """
        Setup ready for comms, opening the requried port
        """

        self.sensor_address = address
        self._open_port()
            
        return
    
    def transcieve_data(self, data):
        """
        Send and receive data
        """
        
        return

    def send_data(self, data):
        """
        Send data on the chosen connection
        """
        return
        
    def read_data_byte(self, byte_addr):
        """
        Read a data byte on the chosen connection
        """
        self.read_address = address
        self.byte_addr = byte_addr
        self._spi_read_byte()

        return

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------

    
    def _open_port(self):
        """
        Open the spi comms port
        """
        print("SPI Comms are not supported")
        log.critical("[COMMS] SPI comms is currently not supported, pleae contact support")
        sys.exit()
        
        #self.connection = ????
        return
    

class Serial_Comms():
    """
    This routine will setup and control the low level comms out to the various
    protocols
    
    By default, it just creates an instance of itself and opens the port
    
    It is required to be given the port to work with, I2C, SPI, SERIAL
    - port is the type of connection I2C, SPI or SERIAL
    - address is the address of the device, default to 0x00 if not required
    """
    
    def __init__(self, address=b'\x00'):
        """
        Setup ready for comms, opening the requried port
        """
        self.sensor_address = address
        self._open_port()
            
        return
    
    def transcieve_data(self, data):
        """
        Send and receive data
        """
        
        return

    def send_data(self, data):
        """
        Send data on the chosen connection
        """
        return
        
    def read_data_byte(self, byte_addr):
        """
        Read a data byte on the chosen connection
        """
        self.read_address = address
        self.byte_addr = byte_addr
        self._serial_read_byte()
        return

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------
        
    def _open_port(self):
        """
        Open the serial comms port
        """
        print("Serial Comms are not supported")
        log.critical("[COMMS] Serial comms is currently not supported, pleae contact support")
        sys.exit()
        
        #self.connection = ????
        return
        

def selftest():
	"""
    Validate the class is working
    
    """
	return

if __name__ == '__main__':
    # setup logging

    
	selftest()

