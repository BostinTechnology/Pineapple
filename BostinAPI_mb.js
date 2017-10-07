var express = require('express');
var app = express();
var http = require('http');
var fs = require('fs');

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data
var AWS = require("aws-sdk");

// moved here so they are available to the functions
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
        
        var params = {
            TableName: 'SensorValues',
            Item: {
                'Device_ID': {'N': packet.device},
                'TimeStamp': {'S': packet.tstamp},
                'Sensor_ID': {'N': packet.sensor},
                'SensorAcroynm': {'S' : packet.acroynm},
                'SensorDescription' : { 'S': packet.desc},
                'MVData': { 'M' : {
                    'type': { 'S' : '1'},
                    'value': { 'S' : packet.data}
                    }},
                'Viewed': { 'BOOL' : false},
                },
        };
        
        console.log("submit params:" + JSON.stringify(params));
        dynamodb.putItem(params, function(err, data) {
            if (err) {
                console.log("submitdata returned an error:" + err);
                res.sendStatus(501);
                
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
            res.sendStatus(501);
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
//    context.fillText("GetItem succeeded"+value_dataset, 30, 70);
//    return value_dataset;
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
            res.sendStatus(501);
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
    //	- DB01 = Local DynamoDB Database 
    //	- DB02 = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nSending data packet to FILESYSTEM");
                console.log(data);
                res.sendStatus(400)
                break;
                
            case "DB01":
                console.log("\nSending data packet to LOCAL DATABASE");
                console.log(packet);

                console.log("\n\nConfiguring connection to local database....");

                var response = get_password(userid, submitdata, res, validate_user);    // Once get_password has finished it calls validate_user

                console.log("get_password response:" + response)
                break;

            case "DB02":
                console.log("\nSending data packet to Amazon AWS");
                console.log(data);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(400);
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
    //	- DB01 = Local DynamoDB Database 
    //	- DB02 = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nGetting data from FILESYSTEM");
                console.log(data);
                res.sendStatus(400)
                break;
                
            case "DB01":
                console.log("\nGetting data from LOCAL DATABASE");
                
                console.log("\n\nConfiguring connection to local database....");

                var response = get_password(userid, retrievesensorvalues, res, validate_user);    // Once get_password has finished it calls validate_user

                console.log("get_password response:" + response)
                break;

            case "DB02":
                console.log("\nGetting data packet from Amazon AWS");
                console.log(data);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(400);
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
    //	- DB01 = Local DynamoDB Database 
    //	- DB02 = Amazon AWS
    // and save data packet to destination


    switch(dest) {
            case "FILE":
                console.log("\nGetting data from FILESYSTEM");
                console.log(data);
                res.sendStatus(400)
                break;
                
            case "DB01":
                console.log("\nGetting data from LOCAL DATABASE");
                
                console.log("\n\nConfiguring connection to local database....");

                var response = get_password(userid, retrievedbversion, res, validate_user);    // Once get_password has finished it calls validate_user

                console.log("get_password response:" + response)
                break;

            case "DB02":
                console.log("\nGetting data packet from Amazon AWS");
                console.log(data);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(400);
        }

    });

var server = app.listen(8080, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Bostin CognIoT API listening at http:// %s :%s", host, port)

})

http.createServer(function (req, res) {
    //res.write(/GetData.html);
    //res.end();
    fs.readFile('GetData.html', function(err, data) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write(data);
    res.end();
  });
}).listen(1227);
