var express = require('express');
var app = express();

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data
var AWS = require("aws-sdk");

// moved here so they are available to the functions as I have no idea how to pass data into functions
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


function get_password (user_name, cb_func, callback) {
    // request the password and using a callback, return it
    var dynamodb = new AWS.DynamoDB();
    
    var docClient = new AWS.DynamoDB.DocumentClient();

    var params = {};
    params.TableName = 'Users';
//        Key: { 
//            "UserName": 'm@mlb.com' //(string | number | boolean | null | Binary)
//            "UserName": "" //(string | number | boolean | null | Binary)
//        },
    params.AttributesToGet = [ 
            'Password',
        ];
    params.ConsistentRead = true;
//    params.Key = {"UserName" : 'm@mlb.com'};
    params.Key = {"UserName : {'S' :" + "m@mlb.com" + "}"};       //{"UserName":{"S":"m@mlb.com"}}
//    params.Key['UserName'] = 'm@mlb.com';
    
    console.log(JSON.stringify(params));
    
    // SHould Be:
    // params:{"TableName":"Users","Key":{"UserName":{"S":"m@mlb.com"}},"AttributesToGet":["Password"],"ConsistentRead":true}
    // gettin:{"TableName":"Users","Key":"UserName : {'S' :m@mlb.com}","AttributesToGet":["Password"],"ConsistentRead":true}
    // gettin:{"TableName":"Users","Key":"{UserName : {'S' :m@mlb.com}}","AttributesToGet":["Password"],"ConsistentRead":true}

    
//    dynamodb.getItem(params, function(err, data) {
    docClient.get(params, function(err, data) {
        if (err) {
            console.log("get_password returned an error:" + err);
        } else
        {
            // this is called when the getItem returns
            console.log("Data:" + JSON.stringify(data, null, 2));
            callback(data, cb_func);     // returns the data to the calling function
        }
    });
    
    console.log("get_password completed");
}

// I think this function should be moved into the app.post response.
function validate_user (db_pwd, callback) {
    // given the database returned obkect, validate it
    console.log("GetItem succeeded:" + JSON.stringify(db_pwd, null, 2));
    console.log("pwd: " + db_pwd.Item.Password);
    console.log("authcode:" + authcode);        // This is empty, should be password passed in
    
    user_auth = db_pwd.Item.Password;
    if (user_auth == authcode) {
        msg = "\tValidated User...."
        console.log(msg);
        callback(true);
        //return false;
        //res.sendStatus(200)
        //res.end();                // this might be in the wrong place
                                    // doesn't work as res is unknown at this position
    }
    else {
        msg = "\tInvalid Authorisation Code";
        console.log(msg);
        //res.sendStatus(403);      // Need to sort out response here to http call.
        //res.end()
        return true;
        }

}

function submitdata(status) {
    // given the status, write the data to the database
    console.log("submitdata reached");
    console.log("Status:"+ status);
    console.log("Payload:" + packet);
    if (status == false) {
        var dynamodb = new AWS.DynamoDB();
        
        var params = {
            TableName: 'SensorValues',
            Item: {
                'Device_ID': {'N': str(device)},
                'TimeStamp': {'S': str(tstamp)},
                'Sensor_ID': {'N': str(sensor)},
                'SensorAcroynm': {'S' : str(acroynm)},
                'SensorDescription' : { 'S': str(desc)},
                'MVData': { 'M' : {
                    'type': { 'S' : '1'},
                    'value': { 'S' : str(data)}
                    }},
                'Viewed': { 'BOOL' : False},
                },
            ConsistentRead: true,
        };
        
        dynamodb.putItem(params, function(err, data) {
            if (err) {
                console.log("get_password returned an error:" + err);
            } else
            {
                // this is called when the putItem returns
                console.log("Data Written successfully??");
            }
        });

    };
    console.log("submitdata completed");

    return;
}
    

app.use(express.static('public'));


app.post('/submitdata', function (req, res, next) {



    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("POST message received as follows: -");

    console.log(req.body);


    //var userid, authcode, dest, datapacket;
    var obj, user_name, user_auth;

    // Here we are going to validate the usernajme sent and only proceed
    //  if the passwword/authcode is correct
     
    userid = req.body.id;
    authcode = req.body.auth;
    dest = req.body.dest;
    packet = req.body.data;

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
                
                //var docClient = new AWS.DynamoDB.DocumentClient();    // Removed MB 160917
                
                var response = get_password(userid, submitdata, validate_user);    // Once get_password has finished it calls validate_user

                break;

            case "DB02":
                console.log("\nSending data packet to Amazon AWS");
                console.log(data);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(400);
    }
                



    console.log("\n /submitdata completed, awaiting callback....");      // This needs to be removed


    // Validate user id and auth code






        //res.end();      // this needs to be removed.
    })


var server = app.listen(8080, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Bostin CognIoT API listening at http:// %s :%s", host, port)

})

