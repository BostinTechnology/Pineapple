#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  testprog.py
#  


import requests
import json

def get_input_status():
    payload = {'id':'555', 'auth':'fredfred'}
    r = requests.get('http://192.168.1.167:8000/validate', params=payload)

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
    r = requests.post('http://192.168.1.167:8000/validate', data=payload)

    if r.status_code ==200:
        print('Header:%s' % r.headers)
        print('Status Code:%s' % r.status_code)
        print('Text:%s' % r.text)
    else:
        print('Failed to Read')
        print('Status Code:%s' % r.status_code)
    return
        
def main():
    
    
    get_input_status()
    
    print('\n\n')
    
    post_input_status()

    
    return

if __name__ == '__main__':
    main()

