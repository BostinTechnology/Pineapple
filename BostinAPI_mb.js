var express = require('express');
var app = express();

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
    

app.use(express.static('public'));


app.post('/submitdata', function (req, res, next) {



    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("POST message received as follows: -");

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
    })


var server = app.listen(8080, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Bostin CognIoT API listening at http:// %s :%s", host, port)

})

