#!/usr/bin/env python3
"""
Testing Routine

This software performs the unit testing of the cls_DataAccessor

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
import requests
import random
from datetime import datetime

#BUG: If this program is in the test directory, it doesn't find this import
from cls_DataAccessor import DataAccessor

DB_LOCAL_ADDR = 'localhost'
DB_LOCAL_PORT = '8080'
DB_AWS_ADDR = '192.168.1.182'
DB_AWS_PORT = '8080'
DB_REMOTE_PORT = '8080'         # Default Value

DB_LOCAL = 'DBLocal'
DB_AWS = 'AWS'
DB_REMOTE = 'DBRemote'


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    logger = logging.getLogger()
    logger.info("[TEST] args passed in:%s" % args)
    logger.info("[TEST] kwargs passed in:%s" % kwargs)

    class MockResponse:
        def __init__(self, status_code, text="", json_data={}):
            self.headers = 'header info'
            self.status_code = status_code
            self.text = text
            self.json_data = json_data

    if args[0] == 'http://localhost:8080/connected':
        logger.debug("[TEST] got to /connected")
        return MockResponse(status_code=200)
    elif args[0] == 'http://localhost:8080/retrievedbversion':
        logger.debug("[TEST] got to /retrievedbversion")
        return MockResponse(status_code=200, text='1.0')
    elif args[0] == 'http://localhost:8080/submitdata':
        logger.debug("[TEST] got to /submitdata with:%s" % kwargs)
        return MockResponse(status_code=200)
    else:
        logger.debug("[TEST] got to unknown")

    return MockResponse(None, 404)



class TestDataAccInit(unittest.TestCase):
    """
    Test the Data Accessor module initialisation

    """
    def setUp(self):
        self.log = logging.getLogger()
        self.log.debug("[Test_DAcc] TestDataAccInit class DataAccessor initialised")
        return

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_init(self, mockpost):
        """
        test the instationisation of the module
        """
        self.log.debug("[TEST] test_init")
        # need to mock _open_port
        result = DataAccessor(customer='m@mlb.com', password='password', db=DB_LOCAL, addr=DB_LOCAL_ADDR, port=DB_LOCAL_PORT,
                        device=1, sensor=2, acroynm="Lght1", desc="Light Sensor 1")

        self.assertIsInstance(result, object)

    #def test_init_fails(self, mock_smbus):
        #"""
        #test the instationisation of the module
        #"""
        #self.log.debug("[TEST] test_init_fails")
        #mock_smbus.side_effect = Exception('FileNotFoundError')

        #with self.assertRaises(SystemExit):
            #result = i2c_comms()            # returns the object i2c_comms

    #TODO: Add in more initialisation tests

class TestDataAccDataIn(unittest.TestCase):
    """
    Test the Data Accessor module Data In

    """

    def setUp(self):
        self.log = logging.getLogger()
        self.log.debug("[Test_DAcc] TestDataAccDataIn class DataAccessor initialised")
        return

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_datain(self, mockpost):
        self.log.debug("[TEST] test_data accessor data in")

        dacc = DataAccessor(customer='m@mlb.com', password='password', db=DB_LOCAL, addr=DB_LOCAL_ADDR, port=DB_LOCAL_PORT,
                        device=1, sensor=2, acroynm="Lght1", desc="Light Sensor 1")
        for i in range(0,10):
            dacc.DataIn(GenerateTestData())
            #TODO: Validate file generated

class TestDataAccTransmitData(unittest.TestCase):
    """
    Test the Data Accessor module Transmit Data

    """

    def setUp(self):
        self.log = logging.getLogger()
        self.log.debug("[Test_DAcc] TestDataAccTransmitData class DataAccessor initialised")
        return

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.post', side_effect=mocked_requests_get)
    def test_transmitdata(self, mockget, mockpost):
        self.log.debug("[TEST] test_data accessor Transmit Data")

        dacc = DataAccessor(customer='m@mlb.com', password='password', db=DB_LOCAL, addr=DB_LOCAL_ADDR, port=DB_LOCAL_PORT,
                        device=1, sensor=2, acroynm="Lght1", desc="Light Sensor 1")
        dacc.TransmitData()


def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """

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
                    'filename': 'Unit_test.log',
                    'mode': 'w'},
            },
        root = {
            'handlers': ['file'],
            'level': logging.DEBUG,
            },
            )

    # Create a logger with the name of the function
    logging.config.dictConfig(log_cfg)
    logger = logging.getLogger()

    logger.info("File Logging Started, current level is %s" % logger.getEffectiveLevel())

    return

def GenerateTimestamp():
    logger = logging.getLogger()
    now = str(datetime.now())
    logger.debug("[TEST] Generated a timestamp %s" % now[:23])
    return now[:23]

def GenerateTestData():
    """
    Generate a dataset to represent the simulated input
    [type, number, units]
    """
    logger = logging.getLogger()
    types = [1,2,3,4]
    units = ['lux', 'Deg C', 'Deg F', '%', 'tag']
    dataset = [[]]
    dataset[0].append(types[random.randint(0,len(types)-1)])
    dataset[0].append(random.randint(0,100))
    dataset[0].append(units[random.randint(0,len(units)-1)])
    dataset[0].append(GenerateTimestamp())
    logger.info("[TEST] Data Being Returned:%s" % dataset)

    return dataset


SetupLogging()

if __name__ == '__main__':
    gbl_log = logging.getLogger()

    gbl_log.critical("\n\n     [TEST] DataAccessor started\n\n")

    unittest.main()

