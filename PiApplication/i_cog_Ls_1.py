#!/usr/bin/env python3

import logging

class iCog():
    
    def __init__(self):
        """
        Initialise the iCog
        """
        print("Into iCog")
        self.log = logging.getLogger()
        self.log.debug("[Ls1] cls_icog initialised")
        return 



def main():
    print("start")
    icog = iCog()
    return

if __name__ == '__main__':
    main()

