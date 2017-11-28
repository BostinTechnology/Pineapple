//
//  Databases
//  DBLocal, AWS, DBRemote - remote is the same as local, bnut indicates the sensor is remote to this device
//
// Response Codes Used
// 200 OK - Standard response for successful HTTP requests
// 400 Bad Request - The server cannot or will not process the request due to an apparent client error
// 403 Forbidden - The request was valid, but the server is refusing action.
// 501 Not Implemented - The server either does not recognize the request method, or it lacks the ability to fulfill the request. Usually this implies future availability (e.g., a new feature of a web-service API)
//
//
// TODO: Check the right http codes are used in the various responses
var express = require('express');
var app = express();
var http = require('http');
var fs = require('fs');

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data
var AWS = require("aws-sdk");

// moved here so they are available to the functions

// These can't live here as they are global scross multiple connections!!
var userid, authcode, dest, packet;
var obj, user_name, user_auth;

app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded

AWS.config.update({
              region: "us-west-2",
              endpoint: "http://localhost:8000",
              accessKeyId: "fakeMyKeyId",
              secretAccessKey: "fakeSecretAccessKey"
            });
var dynamodb = new AWS.DynamoDB();


function get_password (user_name, cb_func, res, callback) {
    // request the password from the db and return it to the callback function with a further callback function to run
    // parameters user_name = user name, 
    // cb_func = the function to pass into the callback when got good data
    // callback = the function to run when the data read completed
    console.log("get_password reached");
    //var dynamodb = new AWS.DynamoDB();
    
    var docClient = new AWS.DynamoDB.DocumentClient();
    
    console.log("User Name being used:" + user_name);
    
    var params = {
        TableName: 'Users',
        Key: { 
            "UserName": user_name
        },
        AttributesToGet: [ 
            'Password'
        ],
        ConsistentRead: true,
    };
    
    console.log("params:"+JSON.stringify(params));
    
    docClient.get(params, function(err, data) {
        if (err) {
            console.log("get_password returned an error:" + err);
            // Need to sort out NEGATIVE response here to http call.
            res.sendStatus(403);
            res.end();
        } else
        {
            // this is called when the getItem returns
            console.log("Data Back:" + JSON.stringify(data, null, 2));
            callback(data, res, cb_func);     // returns the data to the calling function with cb_func as callback
        }
    });
    
    console.log("get_password completed");
}

function validate_user (db_pwd, res, callback) {
    // given the database returned object, validate it
    console.log("validate_user reached")
    console.log("GetItem succeeded:" + JSON.stringify(db_pwd, null, 2));
    // Fails here as .Password doesn't exist
    if (typeof db_pwd.Item.Password == "undefined") {
        console.log("No password returned");
        db_pwd.Item.Password = "";
    }
    console.log("pwd: " + db_pwd.Item.Password);
    console.log("authcode:" + authcode);        // This is empty, should be password passed in

    
    user_auth = db_pwd.Item.Password;
    if (user_auth == authcode) {
        msg = "\tValidated User...."
        console.log(msg);
        callback(true, res);

    }
    else {
        msg = "\tInvalid Authorisation Code";
        console.log(msg);
        res.sendStatus(403);      // Need to sort out NEGATIVE response here to http call.
        res.end()
        }

}

function submitdata(status, res) {
    // given the status, write the data help in the post body (packet) to the database
    console.log("submitdata reached");
    
    if (status == true) {
        // only write the data if status is set to true
        //var dynamodb = new AWS.DynamoDB();
        
//        var params = {
//            TableName: 'SensorValues',
//            Item: {
//                'Device_ID': {'N': packet.device},
//                'TimeStamp': {'S': packet.tstamp},
//                'Sensor_ID': {'N': packet.sensor},
//                'SensorAcroynm': {'S' : packet.acroynm},
//                'SensorDescription' : { 'S': packet.desc},
//                'MVData': { 'M' : {
//                    'type': { 'S' : '1'},
//                    'value': { 'S' : packet.data}
//                    }},
//                'Viewed': { 'BOOL' : false},
//                },
//        };

        var params = {
            TableName: 'SensorValues',
            Item: packet,
        };        
        console.log("submit params:" + JSON.stringify(params));
        dynamodb.putItem(params, function(err, data) {
            if (err) {
                console.log("submitdata returned an error:" + err);
                res.sendStatus(400);
                
            } else
            {
                // this is called when the putItem returns
                console.log("Data Written successfully??");
                // need to return positive here to the http call!!!
                res.sendStatus(200);
                
            }
        });

    };
    console.log("submitdata completed");

    return;
}

function retrievesensorvalues(status, res) {
    // returns a list of the most recent 100 items from the database

    console.log('retrievesensorvalues reached');

    var docClient = new AWS.DynamoDB.DocumentClient();

    var value_dataset = [];
    //context.fillText("Retriving Data", 300, 50);      //debug data
    // TODO: Need to pass in the device_id
    var params = {
        TableName: 'SensorValues',
        KeyConditionExpression: '#name = :value', // a string representing a constraint on the attribute
        ExpressionAttributeNames: { // a map of substitutions for attribute names with special characters
            '#name': 'Device_ID'
        },
        ExpressionAttributeValues: { // a map of substitutions for all attribute values
          ':value': 2480248024
        },
        ScanIndexForward: false,            // return the last xx items
        Limit: 100,
        ProjectionExpression: "MVData",
    };
    docClient.query(params, function(err, data) {
        if (err) {
            console.log("retrievesensorvalues query returned error: " + err);
            res.sendStatus(400);
        } else {
            // The followingline shows how to retrieve just the value I am interested in 
            // Need to loop it through next.
            var dataset = data['Items']; //JSON.stringify(data['Items'], undefined, 2);

            for (var i = 0; i < dataset.length; i = i + 1) {
                value_dataset[i] = dataset[i]['MVData']['value'].valueOf();
            };

            console.log("Data Returned:" + value_dataset);
            res.status(200).send(value_dataset);
            
        }
    });
}


function retrievedbversion(status, res) {
    // retrieves the valid db versions from the database
    console.log('retrievedbversion reached');

    var docClient = new AWS.DynamoDB.DocumentClient();

    var value_dataset = [];
    //context.fillText("Retriving Data", 300, 50);      //debug data
    // TODO: Need to limit the number of values returned
    var params = {
        TableName: 'db_Version',
        KeyConditionExpression: '#name = :value', // a string representing a constraint on the attribute
        ExpressionAttributeNames: { // a map of substitutions for attribute names with special characters
            '#name': 'db_ver'
        },
        ExpressionAttributeValues: { // a map of substitutions for all attribute values
          ':value': 1
        },
        ScanIndexForward: false,            // return the last xx items
        Limit: 100,
        ProjectionExpression: "to_date, from_date, version", 
    };
    docClient.query(params, function(err, data) {
        if (err) {
            console.log("retrievedbversionvalues query returned error: " + err);
            res.sendStatus(400);
        } else {
            // The followingline shows how to retrieve just the value I am interested in 
            // Need to loop it through next.
            var dataset = data['Items'][0]; //JSON.stringify(data['Items'], undefined, 2);
            console.log("Dataset:" + JSON.stringify(dataset, undefined, 2));
            var valid_version = "-1";
            if ( dataset.hasOwnProperty('version')) {
                valid_version = dataset['version'];
            }

            console.log("Version:"+valid_version);

            res.status(200).send(valid_version);
            
        }
    });
//    context.fillText("GetItem succeeded"+value_dataset, 30, 70);
//    return value_dataset;
}

function authenticateuser(status, res) {
    // dummy function at present, just returns a good response
    console.log('authenticateuser reached');
    res.status(200);
    res.end()
}

    
app.use(express.static('public'));


app.post('/submitdata', function (req, res, next) {

    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("submitdata POST message received as follows: -");

    console.log(req.body);

    var obj, user_name, user_auth;

    // convert incoming post to component parts
    userid = req.body.id;
    authcode = req.body.auth;
    dest = req.body.dest;
    packet = JSON.parse(req.body.data);     // This is coming in as a string, needs to be an object
    console.log("userid:"+userid);
    console.log("authcode:" + authcode);
    console.log("dest:" + dest);
    console.log("packet:" + packet);

    //  - Currently supporting the following destinations.
    //	- FILE = Filesystem
    //	- DBLocal = Local DynamoDB Database 
    //	- AWS = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nSending data packet to FILESYSTEM");
                console.log(data);
                res.sendStatus(501);
                break;
                
            case "DBLocal":
            case "DBRemote":
                console.log("\nSending data packet to "+dest+" DATABASE");
                console.log(packet);

                var response = get_password(userid, submitdata, res, validate_user);    // Once get_password has finished it calls validate_user

                break;

            case "AWS":
                console.log("\nSending data packet to Amazon AWS");
                console.log(data);
                res.sendStatus(501);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(501);
    }
                
    console.log("\n /submitdata completed, awaiting callback....");
    });

app.get('/retrievesensorvalues', function (req, res, next) {

    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("retrievesensorvalues GET message received as follows: -");

    console.log(req.body);

    var obj, user_name, user_auth;

    // convert incoming post to component parts
    userid = req.body.id;
    authcode = req.body.auth;
    dest = req.body.dest;
    console.log("userid:"+userid);
    console.log("authcode:" + authcode);
    console.log("dest:" + dest);

    //  - Currently supporting the following destinations.
    //	- FILE = Filesystem
    //	- DBLocal = Local DynamoDB Database 
    //	- AWS = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nGetting data from FILESYSTEM");
                console.log(data);
                res.sendStatus(501)
                break;
                
            case "DBLocal":
            case "DBRemote":
                console.log("\nGetting data packet from "+dest+" DATABASE");
                
                var response = get_password(userid, retrievesensorvalues, res, validate_user);    // Once get_password has finished it calls validate_user

                break;

            case "AWS":
                console.log("\nGetting data packet from Amazon AWS");
                console.log(data);
                res.sendStatus(501);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(501);
        }
    });

app.get('/retrievedbversion', function (req, res, next) {
    // Returns the database version that is currently valid
    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("retrievedbversions GET message received as follows: -");

    console.log(req.body);

    var obj, user_name, user_auth;

    // convert incoming post to component parts
    userid = req.body.id;
    authcode = req.body.auth;
    dest = req.body.dest;
    console.log("userid:"+userid);
    console.log("authcode:" + authcode);
    console.log("dest:" + dest);

    //  - Currently supporting the following destinations.
    //	- FILE = Filesystem
    //	- DBLocal = Local DynamoDB Database 
    //	- AWS = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nGetting data from FILESYSTEM");
                console.log(data);
                res.sendStatus(501)
                break;
                
            case "DBLocal":
            case "DBRemote":
                console.log("\nGetting data packet from "+dest+" DATABASE");
                
                var response = get_password(userid, retrievedbversion, res, validate_user);    // Once get_password has finished it calls validate_user

                break;

            case "AWS":
                console.log("\nGetting data packet from Amazon AWS");
                console.log(data);
                res.sendStatus(501);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(501);
        }

    });

app.get('/connected', function (req, res, next) {
    // Returns a positive response, used to confirm there is connectivity to the client
    // ONly requires the destination to confirm link ok
    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("connected GET message received as follows: -");

    console.log(req.body);

    // convert incoming post to component parts
    dest = req.body.dest;
    console.log("dest:" + dest);

    //  - Currently supporting the following destinations.
    //	- FILE = Filesystem
    //	- DBLocal = Local DynamoDB Database 
    //	- AWS = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nChecking FILESYSTEM enabled");
                console.log(data);
                res.sendStatus(501)
                break;
                
            case "DBLocal":
            case "DBRemote":
                console.log("\nChecking "+dest+" DATABASE enabled");
                res.sendStatus(200);
                break;

            case "AWS":
                console.log("\nChecking Amazon AWS enabled");
                console.log(data);
                res.sendStatus(501);
                
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(501);
        }

    });

app.get('/authenticateuser', function (req, res, next) {
    // Returns the database version that is currently valid
    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("validateuser GET message received as follows: -");

    console.log(req.body);

    var obj, user_name, user_auth, dest;

    // convert incoming post to component parts
    userid = req.body.id;
    authcode = req.body.auth;
    dest = req.body.dest;
    console.log("userid:"+userid);
    console.log("authcode:" + authcode);
    console.log("dest:" + dest);

    //  - Currently supporting the following destinations.
    //	- FILE = Filesystem
    //	- DBLocal = Local DynamoDB Database 
    //	- AWS = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nGetting data from FILESYSTEM");
                console.log(data);
                res.sendStatus(501)
                break;
                
            case "DBLocal":
            case "DBRemote":
                console.log("\nGetting data packet from "+dest+" DATABASE");
                
                var response = get_password(userid, authenticateuser, res, validate_user);    // Once get_password has finished it calls validate_user

                break;

            case "AWS":
                console.log("\nGetting data packet from Amazon AWS");
                console.log(data);
                res.sendStatus(501);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(501);
        }

    });

var server = app.listen(8080, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Bostin CognIoT API listening at http:// %s :%s", host, port)

});

// This section servers up the various web pages that are required on port 1227.
// The first page is capturing the data and storing it in the local store, but
// the displaypage is not displaying it!
http.createServer(function(req, res) {
    console.log("Webserver present on 1227");
  // Homepage
    if (req.url === "/") {
    fs.readFile('login.html', function(err, data) {
        if (err) {
            throw err;
            }
        else {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.write(data);
        res.end();
        }
    });
    }

    // Display data
    else if (req.url.startsWith("/displaydata")) {
        console.log("display data page called");
        fs.readFile('displaydata.html', function(err, data) {
            if (err) {
                throw err;
            }
            else {
                res.writeHead(200, { "Content-Type": "text/html" });
                res.write(data);
                res.end();
            }
    });
    }

    // 404'd!
    else {
      console.log("File not found error");
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("404 error! File not found.");
    };
}).listen(1227);


