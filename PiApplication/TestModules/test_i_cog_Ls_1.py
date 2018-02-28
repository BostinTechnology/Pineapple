#!/usr/bin/env python3
"""

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
from i_cog_Ls_1 import iCog

class TestiCogInit(unittest.TestCase):
    """
    Test the initialisation of the iCog
    - code runs with all sub functions patched
    - code correctly loads the default config

    """
    def setUp(self):
        #SetupLogging()
        self.log = logging.getLogger()
        self.log.debug("[Test_Ls_1] TestiCogInit iCog Ls_1 initialised")
        return

    @patch.object(iCog, '_decode_calib_data')
    @patch.object(iCog, '_setup_sensor')
    def test_init_good_path(self, mock_setup, mock_decode):
        """
        Test the initalisation returns the object correctly
        """
        self.log.info("[TEST] test_init_good_path")

        test_config = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]
        comms = MagicMock()
        mock_decode.return_value = True
        mock_setup.return_value = True
        test_icog = iCog(comms,test_config)
        self.assertIsInstance(test_icog, object)

    @patch.object(iCog, '_decode_calib_data')
    @patch.object(iCog, '_setup_sensor')
    def test_init_decode_fails(self, mock_setup, mock_decode):
        """
        Test that if default fails to load initially, it suceeds second time
        """
        self.log.info("[TEST] test_init_decode_fails")
        test_config = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]
        comms = MagicMock()
        mock_decode.side_effect = [False, True]
        mock_setup.return_value = True
        test_icog = iCog(comms,test_config)
        self.assertIsInstance(test_icog, object)

    @patch.object(iCog, '_decode_calib_data')
    @patch.object(iCog, '_setup_sensor')
    def test_init_decode_fails_twice(self, mock_setup, mock_decode):
        """
        Test that if default fails to load initially, it also fails the second time
        """
        self.log.info("[TEST] test_init_decode_fails_twice")
        test_config = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]
        comms = MagicMock()
        mock_decode.side_effect = [False,False]
        mock_setup.return_value = True
        with self.assertRaises(SystemExit):
            test_icog = iCog(comms,test_config)

class TestiCogConfig(unittest.TestCase):
    """
    Test the default and specific config setup.
    """
    @patch.object(iCog, '_decode_calib_data')
    @patch.object(iCog, '_setup_sensor')
    def setUp(self,mock_setup, mock_decode):
        """
        Test the initalisation returns the object correctly
        """
        #SetupLogging()
        self.log = logging.getLogger()
        self.log.info("[TEST] TestiCogConfig.Setup")

        test_config = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]
        self.comms = MagicMock()
        mock_decode.return_value = True
        mock_setup.return_value = True
        self.test_icog = iCog(self.comms,test_config)

    def tearDown(self):
        """
        Clean up after testing
        """
        self.log.info("[TEST] TestiCogConfig.tearDown")
        self.comms.destroy()

    @patch('builtins.input')
    def test_set_standard_config_good(self, mock_kbd):
        """
        Check it works with valid values
        """
        self.log.info("[TEST] test_set_standard_config_good")
        lp_mode_choices = ['N', 'n', 'Y', 'y']
        freq_choices = ['0.1', '10', '100000', '16416000']

        for lp_mode in lp_mode_choices:
            for freq in freq_choices:
                mock_kbd.side_effect = [lp_mode, freq]
                self.test_icog._set_standard_config()
                config = self.test_icog.ReturnCalibrationData()
                self.log.debug("[TEST] Configuration Generated:\n%s" % config)
                self.assertTrue(len(config)>0, msg="Configuration Data Missing")
                if lp_mode.upper() == 'Y':
                    self.assertTrue(config['low_power_mode'], msg="Expected Low power mode to be set")
                else:
                    self.assertFalse(config['low_power_mode'], msg="Expected Low power mode to be NOT set")
                self.assertTrue(config['read_frequency'] == float(freq), msg="Read Frequency does not match expected")

    @patch('builtins.input')
    def test_set_standard_config_bad(self, mock_kbd):
        """
        Check it works with valid values
        """
        self.log.info("[TEST] test_set_standard_config_bad")
        # Within the lists additional values are added to test only the one question
        lp_mode_choices = ['C', 'v', 'g', '', 'N', '10']
        freq_choices = ['Y', '0.09', '', 'c', '16416001', '10']

        mock_kbd.side_effect = lp_mode_choices
        self.test_icog._set_standard_config()
        config = self.test_icog.ReturnCalibrationData()
        self.log.debug("[TEST] Configuration Generated:\n%s" % config)
        self.assertTrue(len(config)>0, msg="Configuration Data Missing")
        self.assertFalse(config['low_power_mode'], msg="Expected Low power mode to be NOT set")

        mock_kbd.side_effect = freq_choices
        self.test_icog._set_standard_config()
        config = self.test_icog.ReturnCalibrationData()
        self.log.debug("[TEST] Configuration Generated:\n%s" % config)
        self.assertTrue(len(config)>0, msg="Configuration Data Missing")
        self.assertTrue(config['read_frequency'] == 10, msg="Read Frequency does not match expected")

    @patch('builtins.input')
    def test_set_specific_config_good(self, mock_kbd):
        """
        Check it works with valid values
        """
        self.log.info("[TEST] test_set_specific_config_good")
        light_mode_choices = ['a', 'A', 'i', 'I']
        fsr_choices = ['0', '1', '2', '3']
        adc_choices = ['0', '1', '2', '3']

        for light_mode in light_mode_choices:
            for fsr in fsr_choices:
                for adc in adc_choices:
                    mock_kbd.side_effect = [light_mode, fsr, adc]
                    self.test_icog._set_specific_config()
                    config = self.test_icog.ReturnCalibrationData()
                    self.log.debug("[TEST] Configuration Generated:\n%s" % config)
                    self.assertTrue(len(config)>0, msg="Configuration Data Missing")
                    if light_mode.upper() == 'A':
                        self.assertEqual(config['light_mode'],1, msg="Expected Light Mode  to be set")
                    else:
                        self.assertEqual(config['light_mode'], 0, msg="Expected Light Mode to be NOT set")

                    self.assertEqual(config['full_scale_range'], int(fsr), msg="Full Scale Range does not match expected")
                    self.assertEqual(config['adc_resolution'], int(adc), msg="ADC Resolution does not match expected")

    @patch('builtins.input')
    def test_set_specific_config_bad(self, mock_kbd):
        """
        Check it works with valid values
        """
        self.log.info("[TEST] test_set_specific_config_bad")
        # Within the lists, are the other answers to test only the one question at a time
        light_mode_choices = ['s', 'Q', '', 'A', '1', '1']
        fsr_choices = ['A', '-1', '20', '0.1', '4', '3', '3']
        adc_choices = ['A', '3', '-1', '23', '0.1', '4', '2']

        mock_kbd.side_effect = light_mode_choices
        self.test_icog._set_specific_config()
        config = self.test_icog.ReturnCalibrationData()
        self.log.debug("[TEST] Configuration Generated:\n%s" % config)
        self.assertTrue(len(config)>0, msg="Configuration Data Missing")
        self.assertEqual(config['light_mode'], 1, msg="Expected Light Mode to be set")

        mock_kbd.side_effect = fsr_choices
        self.test_icog._set_specific_config()
        config = self.test_icog.ReturnCalibrationData()
        self.log.debug("[TEST] Configuration Generated:\n%s" % config)
        self.assertTrue(len(config)>0, msg="Configuration Data Missing")
        self.assertEqual(config['full_scale_range'], 3, msg="Full Scale Range does not match expected")

        mock_kbd.side_effect = adc_choices
        self.test_icog._set_specific_config()
        config = self.test_icog.ReturnCalibrationData()
        self.log.debug("[TEST] Configuration Generated:\n%s" % config)
        self.assertTrue(len(config)>0, msg="Configuration Data Missing")
        self.assertEqual(config['adc_resolution'], 2, msg="ADC Resolution does not match expected")


#Next is build calib data

#TODO: Write some tests that use the comms handler and patch the smbus
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

SetupLogging()

if __name__ == '__main__':


    gbl_log = logging.getLogger()

    gbl_log.critical("\n\n     [TEST] i2c test comms started\n\n")

    unittest.main()

