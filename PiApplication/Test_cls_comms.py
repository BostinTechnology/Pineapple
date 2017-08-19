#!/usr/bin/env python3
"""
Testing Routine

This software performs the unit testing of the cls_comms - i2c_comms code

"""

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import importlib
import logging
import logging.config
import dict_LoggingSetup

#BUG: If this program is in the test directory, it doesn't find this import
from cls_comms import i2c_comms

class Testi2cCommsInit(unittest.TestCase):
    """
    Test the i2c comms module
    - creates the smbus object
    - stops if it can't create smbus
    
    """
    @patch('smbus.SMBus')
    def test_init(self, mock_smbus):
        """
        test the instationisation of the module
        """
        # need to mock _open_port
        result = i2c_comms()            # returns the object i2c_comms
        
        self.assertIsInstance(result, object)
    
    @patch('smbus.SMBus')
    def test_init_fails(self, mock_smbus):
        """
        test the instationisation of the module
        """
        mock_smbus.side_effect = Exception('FileNotFoundError')
        
        with self.assertRaises(SystemExit):
            result = i2c_comms()            # returns the object i2c_comms
    
class Testi2cComms_read_byte(unittest.TestCase):
    """
    Test the i2c comms module to read a byte
    - address and byte valid
    - invalid byte
    - invalid address
    - invalid byte and address
    - exception thrown
    
    Checking
    - address and byte values correctly passed in
    """
    @patch('smbus.SMBus')
    def Setup(self):
        """
        Setup a temporary connection for the smbus
        """
        self.comms = i2c_comms()
        return
        
    def test_read_addr_byte_valid(self):
        """
        Test the routine with a valid address and byte values
        """
        
        read_data_byte(sens_addr, byte_addr)

    
        
def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """
    global gbl_log
    
    log_cfg = dict(
        version = 1,
        formatters = {
            'full': {'format':
                  '%(asctime)s - %(levelname)-8s - %(message)s',
                  },
            },
        handlers = {
            'file': {'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'full',
                    'level': logging.DEBUG,
                    'filename': 'CognIoT.log',
                    'mode': 'w'},
            },
        root = {
            'handlers': ['file'],
            'level': logging.DEBUG,
            },
            )

    # Create a logger with the name of the function
    logging.config.dictConfig(log_cfg)
    gbl_log = logging.getLogger()

    gbl_log.info("File Logging Started, current level is %s" % gbl_log.getEffectiveLevel)
    
    return

if __name__ == '__main__':
    SetupLogging()
    
    gbl_log.critical("\n\n     [TEST] i2c test comms started\n\n")
    
    unittest.main()

