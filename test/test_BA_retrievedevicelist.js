//
// Test module for BostinAPI_mb.js
//
// Initial version is to try and get some unit testing working
// based on
//    https://www.npmjs.com/package/aws-sdk-mock
//


/** TODO
 * Unable to test for the db not returning, no solution found so far
 *  need to add tests to validate an incorrect data structure
**/
"use strict";

var AWS = require('aws-sdk-mock');

const chai = require('chai');
const expect = require('chai').expect;

chai.use(require('chai-http'));

const app = require('../BostinAPI_mb.js');


var device0 = ["3355054600", 'RPi_3B', 'RPi on workbench']
var device1 = ["165456298", 'RPi_Zero', 'RPi by Cosy Sensor']
var device2 = ["135080095", 'RPi_Sens', 'Rpi on windowsil']
var device3 = ["1234567890", 'RPi_test1', 'RPi test 1 fictitions']
var device4 = ["258963452", 'RPi_test2', 'RPi test 2 fictitions']
var device5 = ["759624153", 'RPi_test3', 'RPi test 3 fictitions']
var dbs = [ "FILE", "DBLocal", "DBRemote", "AWS", "other"]


// Try various database failure combinations, the first is a check it still works
// data['Items']['Devices'][number]['DeviceID'] or ['DeviceAcroynm'] or ['DeviceDescription']
//              'Devices': { 'M' : {
//                    '0' : { 'M' :
//                        {
//                        'DeviceID': { 'S' : str(deviceid)},
//                        'DeviceAcroynm': {'S' : str(acroynm)},
//                        'DeviceDescription': { 'S' : str(description)}
//                        }}
//                    }},
//  /retrievesensorvalues completed
// Raw data returned:{"Items":[{"Devices":{"0":{"DeviceDescription":"RPi on workbench","DeviceAcroynm":"RPi_3B","DeviceID":"3355054600"},"1":{"DeviceDescription":"RPi by Cosy Sensor","DeviceAcroynm":"RPi_Zero","DeviceID":"165456298"},"2":{"DeviceDescription":"Rpi on windowsil","DeviceAcroynm":"RPi_Sens","DeviceID":"135080095"}}}],"Count":1,"ScannedCount":1}
// Retrieve Sensor Values Response:[{"Devices":{"0":{"DeviceDescription":"RPi on workbench","DeviceAcroynm":"RPi_3B","DeviceID":"3355054600"},"1":{"DeviceDescription":"RPi by Cosy Sensor","DeviceAcroynm":"RPi_Zero","DeviceID":"165456298"},"2":{"DeviceDescription":"Rpi on windowsil","DeviceAcroynm":"RPi_Sens","DeviceID":"135080095"}}}]
// Dataset Length:1
// Looping through dataset
// Adding element
// Adding element
// Adding element
// Data Returned:[[{"DeviceDescription":"RPi on workbench","DeviceAcroynm":"RPi_3B","DeviceID":"3355054600"}],[{"DeviceDescription":"RPi by Cosy Sensor","DeviceAcroynm":"RPi_Zero","DeviceID":"165456298"}],[{"DeviceDescription":"Rpi on windowsil","DeviceAcroynm":"RPi_Sens","DeviceID":"135080095"}]]


var response;
var reply, test;

var item;

var rdl_tests = [
    {
        desc: "All Devices (only 2 available), no limit set",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            }}]},
        correct: [ [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                   [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                ],
        code: 200,
        db: "DBLocal",
        qty: 2
    },
    {
        desc: "All Devices (1 available), no limit set",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [ [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                ],
        code: 200,
        db: "DBLocal",
        qty: 1
    },
    {
        desc: "All Devices (6 available) no limit set",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] },
            5: {"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }]
                ],
        code: 200,
        db: "DBLocal",
        qty: 6
    },
    {
        desc: "5 Devices specifically",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                ],
        limit: 5,
        code: 200,
        db: "DBLocal",
        qty: 5
    },
    {
        desc: "2 devices specifically",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],

                ],
        limit: 2,
        code: 200,
        db: "DBLocal",
        qty: 2
    },
    {
        desc: "All Devices as no limit set (16 available)",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] },
            5: {"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            6: {"DeviceID": device0[0], "DeviceAcroynm": device2[1], "DeviceDescription": device1[2] },
            7: {"DeviceID": device1[0], "DeviceAcroynm": device0[1], "DeviceDescription": device2[2] },
            8: {"DeviceID": device2[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            9: {"DeviceID": device3[0], "DeviceAcroynm": device3[1], "DeviceDescription": device3[2] },
            10: {"DeviceID": device4[0], "DeviceAcroynm": device4[1], "DeviceDescription": device4[2] },
            11: {"DeviceID": device5[0], "DeviceAcroynm": device5[1], "DeviceDescription": device5[2] },
            12: {"DeviceID": device3[0], "DeviceAcroynm": device4[1], "DeviceDescription": device5[2] },
            13: {"DeviceID": device4[0], "DeviceAcroynm": device5[1], "DeviceDescription": device3[2] },
            14: {"DeviceID": device5[0], "DeviceAcroynm": device3[1], "DeviceDescription": device4[2] },
            15: {"DeviceID": device3[0], "DeviceAcroynm": device5[1], "DeviceDescription": device4[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device2[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device0[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device3[0], "DeviceAcroynm": device3[1], "DeviceDescription": device3[2] }],
                    [{"DeviceID": device4[0], "DeviceAcroynm": device4[1], "DeviceDescription": device4[2] }],
                    [{"DeviceID": device5[0], "DeviceAcroynm": device5[1], "DeviceDescription": device5[2] }],
                    [{"DeviceID": device3[0], "DeviceAcroynm": device4[1], "DeviceDescription": device5[2] }],
                    [{"DeviceID": device4[0], "DeviceAcroynm": device5[1], "DeviceDescription": device3[2] }],
                    [{"DeviceID": device5[0], "DeviceAcroynm": device3[1], "DeviceDescription": device4[2] }],
                    [{"DeviceID": device3[0], "DeviceAcroynm": device5[1], "DeviceDescription": device4[2] }]

                ],
        code: 200,
        db: "DBLocal",
        qty: 16
    },
    {
        desc: "All Devices as no limit set (1 available)",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                ],
        code: 200,
        db: "DBLocal",
        qty: 1
        },
    {
        desc: "All Devices with a negative limit (-1) set (3 available)",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device3[0], "DeviceAcroynm": device3[1], "DeviceDescription": device3[2] },
            2: {"DeviceID": device4[0], "DeviceAcroynm": device4[1], "DeviceDescription": device4[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device3[0], "DeviceAcroynm": device3[1], "DeviceDescription": device3[2] }],
                    [{"DeviceID": device4[0], "DeviceAcroynm": device4[1], "DeviceDescription": device4[2] }],
                ],
        code: 200,
        limit: -1,
        db: "DBLocal",
        qty: 3
        },
    {
        desc: "5 Devices specifically, with incorrect database structure",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            4: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            9: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            22: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                ],
        limit: 5,
        code: 200,
        db: "DBLocal",
        qty: 5
    },
    {
        desc: "All Devices, with a limit set to a string value",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                ],
        limit: "5",
        code: 200,
        db: "DBLocal",
        qty: 5
    },

    //Different database locations, checking DBRemote still works as expected with a few tests
    {
        desc: "All Devices as no limit set (1 available) for DBRemote",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                ],
        code: 200,
        db: "DBRemote",
        qty: 1
        },
    {
        desc: "2 devices specifically for DBRemote",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],

                ],
        limit: 2,
        code: 200,
        db: "DBRemote",
        qty: 2
    },
    {
        desc: "All Devices (6 available) no limit set for DBRemote",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] },
            5: {"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }]
                ],
        code: 200,
        db: "DBRemote",
        qty: 6
    },
    {
        desc: "Failure response for all Devices (6 available) no limit set for FILE",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] },
            5: {"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }]
                ],
        code: 501,
        db: "FILE",
        qty: 6
    },
    {
        desc: "Failure response for all Devices (6 available) no limit set for AWS",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] },
            5: {"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }]
                ],
        code: 501,
        db: "AWS",
        qty: 6
    },
    {
        desc: "Failure response for all Devices (6 available) no limit set for other",
        resp: { "Items": [{ "Devices": {
            0: {"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            1: {"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] },
            2: {"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] },
            3: {"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] },
            4: {"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] },
            5: {"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] },
            }}]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }]
                ],
        code: 501,
        db: "other",
        qty: 6
    },

// Incorrect data structures
    {
        // TODO: This test is not complete
        desc: "Incorrect data structure in database",
        resp:  { "Items": [{ "Devices": "" }]},
        correct: [  [{"DeviceID": device0[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device1[1], "DeviceDescription": device1[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device2[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device0[0], "DeviceAcroynm": device1[1], "DeviceDescription": device2[2] }],
                    [{"DeviceID": device1[0], "DeviceAcroynm": device2[1], "DeviceDescription": device0[2] }],
                    [{"DeviceID": device2[0], "DeviceAcroynm": device0[1], "DeviceDescription": device0[2] }]
                ],
        code: 200,
        db: "DBRemote",
        qty: 6
    },


];
 
rdl_tests.forEach( function(test) {

    describe('TEST API endpoint /retrievedevicelist, TEST correct data structure using limit', function() {
        // Unit test the retrieve device list functionality for multiple users
        // No need to authenticate users as this has already been proven
        // Checks for correct data content and quantity of readings

        after(function() {
            // stuff to do after the test has run
            AWS.restore('DynamoDB.DocumentClient');
        });

        beforeEach(function() {
            // Stuff to do before the test runs
            // Mock the user authentication - this has been validated elsewhere
            AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
                response = { "Item": {"Password" : "pssaword"}};      // Data format response is ['Item']['Password'] = password
                callback(null, response);
            });

            AWS.mock('DynamoDB.DocumentClient', 'query', function (params, callback) {
                response = test.resp;        
                callback(null, response);
            });
        });


        it('should validate that '+test.desc+' are returned is complete', function() {
            return chai.request(app)
            .get('/retrievedevicelist')
            .send({dest: test.db, id: "l@mlb.com", auth: "pssaword", limit: test.limit})
            .catch(err => err.response)
            .then(function(res) {
                reply = JSON.parse(res.text)
                expect(res).to.have.status(test.code);
                console.log("res.text:"+reply);
                console.log("correct :"+test.correct);
                console.log("length of response"+reply.length);
                console.log("Expected length"+test.qty);
                expect(reply).to.deep.equal(test.correct);
                expect(reply.length).to.equal(test.qty);
                });
            }
        )
    })
});

describe('TEST API endpoint /retrievedevicelist, error response from dynamodb', function() {
    // Test the retrieve db version functionality for when there are database issues.
    // checks for database errors / bad responses

    // no version record, should return 200 with a version of -1
    
    before(function() {
        // Stuff to do before the test runs
        // Mock the user authentication - this has been validated elsewhere
        AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
            var response = { "Item": {"Password" : "pssaword"}};      // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });

        // Mock the database response
        AWS.mock('DynamoDB.DocumentClient', 'query', function (params, callback) {
            callback(400, null);
        });
    });

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    // successful response with valid user - DBLocal
    it('should return an error code 400', function() {
        return chai.request(app)
        .get('/retrievedevicelist')
        .send({dest: 'DBLocal', id:'l@mlb.com', auth:'pssaword'})
        .catch(err => err.response)
        .then(function(err) {
            expect(err).to.have.status(400);
        });
    });

});



