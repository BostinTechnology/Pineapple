#!/usr/bin/env python3
"""
Testing Routine

This software performs the unit testing of the cls_comms - i2c_comms code

"""

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import call
import importlib
import logging
import logging.config
import dict_LoggingSetup
import subprocess

#BUG: If this program is in the test directory, it doesn't find this import
from cls_comms import i2c_comms

@patch('smbus.SMBus')
class Testi2cCommsInit(unittest.TestCase):
    """
    Test the i2c comms module
    - creates the smbus object
    - stops if it can't create smbus

    """
    def test_init(self, mock_smbus):
        """
        test the instationisation of the module
        """
        gbl_log.debug("[TEST] test_init")
        # need to mock _open_port
        result = i2c_comms()            # returns the object i2c_comms

        self.assertIsInstance(result, object)

    def test_init_fails(self, mock_smbus):
        """
        test the instationisation of the module
        """
        gbl_log.debug("[TEST] test_init_fails")
        mock_smbus.side_effect = Exception('FileNotFoundError')

        with self.assertRaises(SystemExit):
            result = i2c_comms()            # returns the object i2c_comms

class Testi2cCommsRepeatedStart(unittest.TestCase):
    """
    Test the repeated start is set correctly.
    This is achieved on the Pi manually by
    1. Navigate to /sys/module/i2c_bcm2708/parameters
    2. Modify 'combined'
        sudo nano combined
        change N to Y
        Save and Exit
    Command to run as Superuser is
        echo -n 1 > /sys/module/i2c_bcm2708/parameters/combined

    two tests,
    - not set initially
    - set after call
    """
    def test_repeated_start_not_set(self):
        """
        Check the repeated start setting is correct
        """
        gbl_log.debug("[TEST] test_repeated_start_not_set")
        result = ''
        comms = i2c_comms()
        response = comms.repeated_start(repeated=False)
        with open('/sys/module/i2c_bcm2708/parameters/combined', 'r') as check:
            result = check.read(1)
        self.assertEqual(result, 'N')
        self.assertTrue(response)

    def test_repeated_start_set(self):
        """
        Check the repeated start setting is correct
        """
        gbl_log.debug("[TEST] test_repeated_start_set")
        result = ''
        comms = i2c_comms()
        response = comms.repeated_start(repeated=True)
        with open('/sys/module/i2c_bcm2708/parameters/combined', 'r') as check:
            result = check.read(1)
        self.assertEqual(result, 'Y')
        self.assertTrue(response)

@patch('smbus.SMBus')
class Testi2cComms_read_byte(unittest.TestCase):
    """
    Test the i2c comms module to read a byte
    - address and byte valid
    - exception thrown

    Checking
    - address and byte values correctly passed in
    """

    def test_read_addr_byte_valid(self, mock_smbus):
        """
        Test the routine with a valid address and byte values
        """
        gbl_log.debug("[TEST] test_read_addr_byte_valid")
        mock_smbus().read_byte_data.return_value = 0x45

        comms = i2c_comms()
        result = comms.read_data_byte(0x60, 0x10)
        mock_smbus().read_byte_data.assert_called_with(0x60, 0x10)
        self.assertEqual(result, 0x45)

    def test_read_addr_byte_exception(self, mock_smbus):
        """
        Test the routine with an exception raised
        """
        #BUG: Need to check the exception raised

        gbl_log.debug("[TEST] test_read_addr_byte_exception")
        mock_smbus().read_byte_data.side_effect = Exception('IOError')

        comms = i2c_comms()
        result = comms.read_data_byte(0x50, 0x16)
        mock_smbus().read_byte_data.assert_called_with(0x50, 0x16)

        self.assertEqual(result, 0)

@patch('smbus.SMBus')
class Testi2cComms_read_data_bytes(unittest.TestCase):
    """
    Test the i2c comms module to read a range of bytes
    - address and bytes are valid
    - returns empty list if any of the replies are invalid
    - handles exception
    parameters(sens_addr, start_byte, no_bytes)
    """

    def test_read_addr_bytes_valid(self, mock_smbus):
        """
        Test the routine with a valid range of bytes
        Request a range and check
        """
        gbl_log.debug("[TEST] test_read_addr_bytes_valid")
        mock_smbus().read_byte_data.side_effect = [0x26, 0x27, 0x28]
        calls = [call(0x45, 0x12),call(0x45, 0x13),call(0x45, 0x14)]
        comms = i2c_comms()
        result = comms.read_data_bytes(0x45, 0x12, 3)
        mock_smbus().read_byte_data.assert_has_calls(calls)
        self.assertEqual(result, [0x26, 0x27, 0x28])

    def test_read_addr_bytes_exception(self, mock_smbus):
        """
        Test the routine with an exception raised whilst reading each address and byte values
        """
        #BUG: Need to check the exception raised

        gbl_log.debug("[TEST] test_read_addr_bytes_exception")
        mock_smbus().read_byte_data.side_effect = [Exception('IOError'), 0x26, 0x27]
        calls = [call(0x45, 0x12),call(0x45, 0x13),call(0x45, 0x14)]
        comms = i2c_comms()
        result = comms.read_data_bytes(0x45, 0x12, 3)
        mock_smbus().read_byte_data.assert_has_calls(calls)
        self.assertEqual(result, [])

        mock_smbus().read_byte_data.side_effect = [0x26, Exception('IOError'), 0x27]
        calls = [call(0x45, 0x12),call(0x45, 0x13),call(0x45, 0x14)]
        comms = i2c_comms()
        result = comms.read_data_bytes(0x45, 0x12, 3)
        mock_smbus().read_byte_data.assert_has_calls(calls)
        self.assertEqual(result, [])

        mock_smbus().read_byte_data.side_effect = [0x26, 0x27, Exception('IOError')]
        calls = [call(0x45, 0x12),call(0x45, 0x13),call(0x45, 0x14)]
        comms = i2c_comms()
        result = comms.read_data_bytes(0x45, 0x12, 3)
        mock_smbus().read_byte_data.assert_has_calls(calls)
        self.assertEqual(result, [])

@patch('smbus.SMBus')
class Testi2cComms_write_byte(unittest.TestCase):
    """
    Test the i2c comms module to write a byte
    - address and byte and value valid
    - exception thrown

    Checking
    - address and byte values correctly passed in
    """

    def test_write_addr_byte_valid(self, mock_smbus):
        """
        Test the routine with a valid address and byte values
        """
        gbl_log.debug("[TEST] test_write_addr_byte_valid")
        mock_smbus().write_byte.return_value = True

        comms = i2c_comms()
        result = comms.write_data_byte(0x60, 0x10, 0x80)
        mock_smbus().write_byte_data.assert_called_with(0x60, 0x10, 0x80)
        self.assertEqual(result, True)

    def test_write_addr_byte_exception(self, mock_smbus):
        """
        Test the routine with an exception raised
        """
        #BUG: Need to check the exception raised

        gbl_log.debug("[TEST] test_write_addr_byte_exception")
        mock_smbus().write_byte.side_effect = Exception('IOError')

        comms = i2c_comms()
        result = comms.write_data_byte(0x50, 0x16, 0xff)
        mock_smbus().write_byte_data.assert_called_with(0x50, 0x16, 0xff)

        self.assertEqual(result, True)

@patch('smbus.SMBus')
class Testi2cComms_write_data_bytes(unittest.TestCase):
    """
    Test the i2c comms module to write a range of bytes
    - address and bytes and values are valid
    - handles exception
    """

    def test_write_addr_bytes_valid(self, mock_smbus):
        """
        Test the routine with a valid range of bytes
        Request a range and check
        """
        gbl_log.debug("[TEST] test_write_addr_bytes_valid")
        mock_smbus().write_byte_data.side_effect = [True, True, True]
        calls = [call(0x45, 0x12, 0x20),call(0x45, 0x13, 0x21),call(0x45, 0x14, 0x22)]
        comms = i2c_comms()
        result = comms.write_data_bytes(0x45, 0x12, [0x20, 0x21, 0x22])
        mock_smbus().write_byte_data.assert_has_calls(calls)
        self.assertEqual(result, True)

    def test_write_addr_bytes_exception(self, mock_smbus):
        """
        Test the routine with an exception raised whilst writing each address and byte values
        """
        #BUG: Need to check the exception raised
        gbl_log.debug("[TEST] test_write_addr_bytes_exception")
        mock_smbus().write_byte_data.side_effect = Exception('IOError')
        comms = i2c_comms()
        result = comms.write_data_bytes(0x45, 0x12, [0x33, 0x34, 0x35])
        mock_smbus().write_byte_data.assert_called_with(0x45, 0x12, 0x33)
        self.assertEqual(result, False)

        mock_smbus().write_byte_data.side_effect = [True, Exception('IOError')]
        calls = [call(0x45, 0x12, 0x33),call(0x45, 0x13, 0x34)]
        comms = i2c_comms()
        result = comms.write_data_bytes(0x45, 0x12, [0x33, 0x34, 0x35])
        mock_smbus().write_byte_data.assert_has_calls(calls)
        self.assertEqual(result, False)


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

