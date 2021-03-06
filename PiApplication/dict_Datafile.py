"""
This file contains the information about the sensors.

Structure of each subset of data

['iCog file','iCog name','iCog type','iCog Manufacturer', Sensor type code 1, Senor type code 2]

The sensor type code is referenced in the EEPROM data model

"""

datafile = [
    ['i_cog_Ps_1','i-cog.Ps.1','Pressure / Altitude','ST LPS25HB',0x01,0x01],
    ['i_cog_Ps_2','i-cog.Ps.2','Pressure / Altitude','Bosch',0x01,0x02],
    ['i_cog_Ps_3','i-cog.Ps.3','Pressure / Altitude','Freescale',0x01,0x03],
    ['i_cog_Ls_1','i-cog.Ls.1','Light','Intersil',0x02,0x01],
    ['i_cog_Ls_2','i-cog.Ls.2','Light','Vishay UV',0x02,0x02],
    ['i_cog_Ls_3','i-cog.Ls.3','Light','Vishay VCNL4040',0x02,0x03],
    ['i_cog_Ts_1','i-cog.Ts.1','Temperature','ST HTS221',0x03,0x01],
    ['i_cog_Ts_2','i-cog.Ts.2','Temperature','Measurement Specialities',0x03,0x02],
    ['i_cog_Ts_3','i-cog.Ts.3','Temperature','TI HDC1008',0x03,0x03],
    ['i_cog_Rs_1','i-cog.Rs.1','Rate Sensor','Bosch',0x04,0x01],
    ['i_cog_Rs_2','i-cog.Rs.2','Rate Sensor','Freescale MMA8652FC',0x04,0x02],
    ['i_cog_Rs_3','i-cog.Rs.3','Rate Sensor','ST LIS3DH',0x04,0x03],
    ['i_cog_Rs_4','i-cog.Rs.4','Rate Sensor','Freescale FXAS21002C',0x04,0x04],
    ['i_cog_Rs_5','i-cog.Rs.5','Rate Sensor','Freescale FXOS8700CQ',0x04,0x05],
    ]

