#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  testprog.py
#  


import requests
import json
import time
from datetime import datetime

data_record = {}
data_record['UserName'] = { 'S' : 'm@mlb.com'}
#data_record['Password'] = { 'N' : 'password'}

#API_ADDRESS = 'http://RPi_Display:8080'
API_ADDRESS = 'http://localhost:8080'

def GenerateTimestamp():
    now = str(datetime.now())
    print("[DAcc] Generated a timestamp %s" % now[:23])
    return now[:23]
    
def submitdata():
    # {'MVData': {'M': {'value': {'S': '50.78125'}, 'units': {'S': 'lx'}, 'type': {'S': '1'}}},
    # 'Viewed': {'BOOL': False}, 'Sensor_ID': {'N': '1'}, 'SensorDescription': {'N': 'light sensor in office'},
    # 'SensorAcroynm': {'N': 'lght1'}, 'TimeStamp': {'S': '2017-10-11 21:02:17.907'}, 'Device_ID': {'N': '3355054600'}}
    #payload = {'device':'12345678', 'tstamp':'20-09-2017 :15:05:34.000', 'sensor':'1',
    #    'acroynm':'mb_test', 'desc':'sensor via RESTFul API', 'data':'-0.1 Deg C'}
    payload = {'MVData': {'M': {'value': {'S': '-99.9999'}, 'units': {'S': 'lx'}, 'type': {'S': '1'}}},
               'Viewed': {'BOOL': False}, 'Sensor_ID': {'N': '1'}, 'SensorDescription': {'S': 'light sensor in office'},
               'SensorAcroynm': {'S': 'lght1'}, 'TimeStamp': {'S': GenerateTimestamp()},
               'Device_ID': {'N': '3355054600'}}
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal', 'data': json.dumps(payload)}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.post(API_ADDRESS+'/submitdata', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return

def submitdata_false():
    # {'MVData': {'M': {'value': {'S': '50.78125'}, 'units': {'S': 'lx'}, 'type': {'S': '1'}}},
    # 'Viewed': {'BOOL': False}, 'Sensor_ID': {'N': '1'}, 'SensorDescription': {'N': 'light sensor in office'},
    # 'SensorAcroynm': {'N': 'lght1'}, 'TimeStamp': {'S': '2017-10-11 21:02:17.907'}, 'Device_ID': {'N': '3355054600'}}
    #payload = {'device':'12345678', 'tstamp':'20-09-2017 :15:05:34.000', 'sensor':'1',
    #    'acroynm':'mb_test', 'desc':'sensor via RESTFul API', 'data':'-0.1 Deg C'}
    payload = {'MVData': {'M': {'value': {'S': '-99.9999'}, 'units': {'S': 'lx'}, 'type': {'S': '1'}}},
               'Viewed': {'BOOL': False}, 'Sensor_ID': {'N': '1'}, 'SensorDescription': {'S': 'light sensor in office'},
               'SensorAcroynm': {'S': 'lght1'}, 'TimeStamp': {'S': GenerateTimestamp()},
               'Device_ID': {'N': '3355054600'}}
    fulldata = {'id':'m@mlb.com', 'auth':'wrongpwd', 'dest':'DBLocal', 'data': json.dumps(payload)}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.post(API_ADDRESS+'/submitdata', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
    
def retrievesensorvalues():
    print("Retreiving Sensor Values")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal', 'device_id' : '165456298'} #'3355054600'} 
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/retrievesensorvalues', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
    
def retrievelimitsensorvalues():
    print("Retreiving Sensor Values")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal', 'device_id' : '165456298',
                'limit':50} #'3355054600'} 
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/retrievesensorvalues', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
    
def retrievetimesensorvalues():
    print("Retreiving Sensor Values")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal', 'device_id' : '165456298',
                'starttime': '2017-12-25 13:05:05'} #'3355054600'} 
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/retrievesensorvalues', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
    
def retrievedevicelist():
    print("Retreiving Devices List")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal'}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/retrievedevicelist', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)

    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return

def retrievedbversion():
    print("Retrieving Database Version info")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal'}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/retrievedbversion', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return

def connected():
    print("Checking connectivity")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal'}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/connected', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return

def authenticateuser():
    print("Authenticating User")
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal'}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get(API_ADDRESS+'/authenticateuser', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
        
def main():
    
    
    #connected()

    #authenticateuser()
    
    #submitdata()

    #submitdata_false()

    retrievesensorvalues()

    retrievelimitsensorvalues()

    retrievetimesensorvalues()

    #retrievedbversion()

    #retrievedevicelist()
    
    return

if __name__ == '__main__':
    main()

