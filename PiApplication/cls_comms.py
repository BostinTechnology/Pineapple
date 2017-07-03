#!/usr/bin/env python3
"""
cls_comms
performs all the low level comms required for the various devices.

Requires sudo apt-get install python3-smbus

"""
#Bus types

import smbus
import serial
import sys
import logging
import time

import Standard_Settings as SS

#TODO: Add a retry loop on the comms routines with a default counter set here.

#TODO: Convert the fixed time below to a variable that is passed in or derived in some manner.
# The minimum time between consecutive writes.
I2C_WRITE_DELAY = 0.005

class i2c_comms():
    """
    This routine will setup and control the low level comms out to the various
    protocols
    
    By default, it just creates an instance of itself and opens the port

    """
    
    def __init__(self):
        """
        Setup ready for comms, opening the requried port
        """
        self.log = logging.getLogger()
        self._open_port()

        self.log.debug("[I2C COMMS] Class initiated")

            
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
        
    def read_data_byte(self, sens_addr, byte_addr):
        """
        Read a data byte on the chosen connection
        """

        reply = self._read_byte(sens_addr, byte_addr)
        return reply
    
    def read_data_bytes(self, sens_addr, start_byte, no_bytes):
        """
        Read a quantity of bytes, starting from start byte
        So passing (0x50, 0x10, 5) will return values from bytes
            0x10, 0x11, 0x12, 0x13, 0x14
        returns a list of values or an empty string if error occurred
        """
        self.log.info("[I2C COMMS] Read Data Bytes from address %s starting at %s for %s bytes" 
                        % (sens_addr, start_byte, no_bytes))
        response = []
        for byte in range(start_byte, start_byte+no_bytes):
            reply = self._read_byte(sens_addr, byte)
            if reply != '':
                response.append(reply)
            else:
                response = []
                self.log.debug("[I2C COMMS] Response received from sensor failed, returned:%s" % response)
                break
        self.log.debug("[I2C COMMS] Data bytes returned: %s" % response)
        return response

    def write_data_bytes(self, sens_addr, start_byte, data_bytes):
        """
        Write a quantity of bytes, starting from start byte
        So passing (0x50, 0x10, [0x34, 0x45, 0x56]) will write values into bytes
            0x10=0x34, 0x11=0x45, 0x12=0x56
        returns confirmation
        """
        self.log.info("[I2C COMMS] Write Data Bytes to address %s starting at %s with bytes %s" 
                        % (sens_addr, start_byte, data_bytes))
        response = False
        addr = start_byte
        for byte in data_bytes:
            self.log.debug("[I2C COMMS] Data:%s to be written to:%s for device:%s" %(byte, addr, sens_addr))
            response = self._write_byte(sens_addr, addr, byte)
            if response == False:
                break
            addr = addr + 1
            time.sleep(I2C_WRITE_DELAY)
        return response
            
    def write_data_byte(self, sens_addr, addr_byte, data_byte):
        """
        Write a byte to the address byte
        So passing (0x50, 0x10, 0x34) will write 0x34 into address byte 0x10
        returns confirmation
        """
        self.log.info("[I2C COMMS] Write Data Byte to address %s byte %s with value %s" 
                        % (sens_addr, addr_byte, data_byte))
        response = self._write_byte(sens_addr, addr_byte, data_byte)
        return response
        
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
            self.log.critical("[I2C COMMS] Unable to open comms port using smbus (_i2c_port), program halted")
            self.log.exception("[I2C COMMS] _write_byte Exception Data")
            print("\nError Occurred, program halted - contact support\n")
            sys.exit()
        self.log.info("[I2C COMMS] I2C connection created:%s" % self.connection)
        return
    
    def _read_byte(self, addr, byte_no):
        """
        Read a byte from the given address, returns either the value read or an empty binary string
        """
        value = 0
        try:
            value = self.connection.read_byte_data(addr, byte_no)
        except:
            self.log.warning("[I2C COMMS] Unable to read byte:%s from i2c device:%s and got this response:%s"
                %(byte_no, addr, value))
            self.log.exception("[I2C COMMS] _read_byte Exception Data")
            value = ''
        self.log.info("[I2C COMMS] Read Byte from address:%s from i2c device:%s and got this response:%s" 
                        % (byte_no, addr, value))
        return value
    
    def _write_byte(self, addr, byte_no, value):
        """
        Write a byte from the given address.
        The only response is an exception
        """
        response = False
        try:
            self.connection.write_byte_data(addr, byte_no, value)
        except:
            self.log.warning("[I2C COMMS] Unable to write byte:%s of value:%s from i2c device:%s"
                %(byte_no, value, addr))
            self.log.exception("[I2C COMMS] _write_byte Exception Data")
        else:
            self.log.info("[I2C COMMS] Write to Byte:%s of value:%s for i2c device:%s" 
                        % (byte_no, value, addr))
            response = True
        return response    


class SPi_comms():
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
        self.log = logging.getLogger()

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
        self.log.critical("[COMMS] SPI comms is currently not supported, pleae contact support")
        sys.exit()
        
        #self.connection = ????
        return
    

class Serial_comms():
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
        self.log = logging.getLogger()
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
        self.log.critical("[COMMS] Serial comms is currently not supported, pleae contact support")
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

