var express = require('express');
var app = express();

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data
var AWS = require("aws-sdk");

app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded

AWS.config.update({
              region: "us-west-2",
              endpoint: "http://localhost:8000",
              accessKeyId: "fakeMyKeyId",
              secretAccessKey: "fakeSecretAccessKey"
            });
var dynamodb = new AWS.DynamoDB();

//var get_password = function(user_name, callback) {

    //var docClient = new AWS.DynamoDB.DocumentClient();
    
    //var params = {
        //TableName: 'Users',
        //Key: { 
            //"UserName": user_name, //(string | number | boolean | null | Binary)
        //},
        //AttributesToGet: [ 
            //'UserName',
            //'Client_ID',
            //'Password',
        //],
        //ConsistentRead: true,
    //};
    
    //docClient.get(params, callback);
    //console.log("get_password completed")
//}

//function get_password (user_name) {
    
    //return new Promise(function (resolve, reject) {

        //var docClient = new AWS.DynamoDB.DocumentClient();
        
        //var params = {
            //TableName: 'Users',
            //Key: { 
                //"UserName": 'm@mlb.co.uk' //(string | number | boolean | null | Binary)
            //},
            //AttributesToGet: [ 
                //'Password'
            //],
            //ConsistentRead: true,
        //};
        
        //var dataPromise = docClient.get(params).promise() ;
        //dataPromise.then(function(data) {
            //console.log("Promise"+JSON.stringify(data, null, 2));
        //}).catch(function(err) {
            //console.log("Promise ERROR:"+err);
        //});
        
        //console.log("get_password completed");
    //});
//}

function get_password (user_name, res) {

    var dynamodb = new AWS.DynamoDB();
    
    var params = {
        TableName: 'Users',
        Key: { 
            "UserName": { 'S' : 'm@mlb.co.uk'} //(string | number | boolean | null | Binary)
        },
        AttributesToGet: [ 
            'Password'
        ],
        ConsistentRead: true,
    };
    
    dynamodb.getItem(params, function(err, data) {
    if (err) {
        console.log("Error:" + err);
        return "error"
    }
    else {
        console.log("Data:" + data);
        res.send(JSON.stringify(data, underfined, 2));
        res.end()
        //return "hello"
    }
    });
    
    console.log("get_password completed");
}


app.use(express.static('public'));


app.post('/submitdata', function (req, res, next) {



    console.log("******************************************");
    console.log(" RUNNING MB VERSION");
    console.log("POST message received as follows: -");

    console.log(req.body);


    var userid, authcode, dest, datapacket;
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
                break;
                
            case "DB01":
                console.log("\nSending data packet to LOCAL DATABASE");
                console.log(packet);

                console.log("\n\nConfiguring connection to local database....");
                
                //
                
                var dynamodb = new AWS.DynamoDB();
    
                var params = {
                    TableName: 'Users',
                    Key: { 
                        "UserName": { 'S' : 'm@mlb.co.uk'} //(string | number | boolean | null | Binary)
                    },
                    AttributesToGet: [ 
                        'Password'
                    ],
                    ConsistentRead: true,
                };
                
                // tried both docClient and dynamodb, no difference
                
                dynamodb.getItem(params, function(err, data) {
                if (err) {
                    console.log("Error:" + err);
                    next(err)
                }
                else {
                    console.log("Response:"+data)
                    if (!data.Attributes) {
                        res.status(404).end();
                    } else {
                        res.send()
                    }
                    //return "hello"
                }
                });
                
                console.log("get_password completed");
                
                //
                //console.log("Response:"+response);

                break;

            case "DB02":
                console.log("\nSending data packet to Amazon AWS");
                console.log(data);
                break;

            default:
                console.log("\n\nERROR : Unrecognised destination");
                res.sendStatus(400);
    }
                



    console.log("\nIdentifying User....");


    // Validate user id and auth code






        res.end();
    })


var server = app.listen(8080, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Bostin CognIoT API listening at http:// %s :%s", host, port)

})

