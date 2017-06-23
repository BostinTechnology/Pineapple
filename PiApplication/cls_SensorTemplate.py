"""

This is a template class, it is created to develop the template for the
sensors to actually be based on


BUG - Logging is not working

TODO: Will need to check the minimum revision of the software
        #BUG - This should be set higher, but is changed for testing
        self.readfrequency = 3
        log.debug("iCOG initialised, read frequency set to %s" % self.readfrequency)

"""

import logging

import Standard_Settings



def SetupHardware(uuid, bustype, busnumber, sensoraddress):
    """
    
    The real routine sets up the comms for the sensor attached to the PI
    This just returns a positive status and an object representing the sensor
    
    """
    log = logging.getLogger(__name__)
    #TODO: needs to return an instance of iteself
    log.info("Setting Up Hardware")
    
    return True

def ReadData(uuid, bustype, busnumber, deviceaddress):
    """
    
    The real routine sets up the comms for the sensor attached to the PI
    This just returns a positive status and an object representing the sensor
    
    """
    log = logging.getLogger(__name__)
    sensor_data = {"0.01", "35"}
    
    return True, sensor_data
