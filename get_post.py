#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  testprog.py
#  


import requests
import json

data_record = {}
data_record['UserName'] = { 'S' : 'm@mlb.com'}
#data_record['Password'] = { 'N' : 'password'}


def get_input_status():
    payload = {'id':'555', 'auth':'fredfred'}
    r = requests.get('http://192.168.1.182:8000/validate', params=payload)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return

def post_input_status():
    payload = {'id':'666', 'auth':'password'}
#    r = requests.post('http://192.168.1.109:8000/validate', data=json.dumps(payload))  # For json accepted API
    r = requests.post('http://192.168.1.182:8000/validate', data=payload)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return

def post_data():
    payload = {'id':'666', 'auth':'password', 'dest':'DBLocal', 'data':'this is the data'}
    r = requests.post('http://192.168.1.182:8000/validate', data=payload)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
    
def submitdata():
    # {'MVData': {'M': {'value': {'S': '50.78125'}, 'units': {'S': 'lx'}, 'type': {'S': '1'}}},
    # 'Viewed': {'BOOL': False}, 'Sensor_ID': {'N': '1'}, 'SensorDescription': {'N': 'light sensor in office'},
    # 'SensorAcroynm': {'N': 'lght1'}, 'TimeStamp': {'S': '2017-10-11 21:02:17.907'}, 'Device_ID': {'N': '3355054600'}}
    #payload = {'device':'12345678', 'tstamp':'20-09-2017 :15:05:34.000', 'sensor':'1',
    #    'acroynm':'mb_test', 'desc':'sensor via RESTFul API', 'data':'-0.1 Deg C'}
    payload = {'MVData': {'M': {'value': {'S': '50.78125'}, 'units': {'S': 'lx'}, 'type': {'S': '1'}}},
               'Viewed': {'BOOL': False}, 'Sensor_ID': {'N': '1'}, 'SensorDescription': {'N': 'light sensor in office'},
               'SensorAcroynm': {'N': 'lght1'}, 'TimeStamp': {'S': '2017-10-11 21:02:17.907'},
               'Device_ID': {'N': '3355054600'}}
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal', 'data': json.dumps(payload)}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.post('http://RPi_3B:8080/submitdata', data=fulldata)

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
    fulldata = {'id':'m@mlb.com', 'auth':'password', 'dest':'DBLocal'}
    print("Payload Being Sent:\n%s" % fulldata)
    r = requests.get('http://RPi_3B:8080/retrievesensorvalues', data=fulldata)

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
    r = requests.get('http://RPi_3B:8080/retrievedbversion', data=fulldata)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return



        
def main():
    
    
    #get_input_status()
    
    #print('\n\n')
    
    #post_input_status()

    #print('\n\n')
    
    #post_data()
    
    submitdata()

    #retrievesensorvalues()

    #retrievedbversion()
    
    return

if __name__ == '__main__':
    main()

