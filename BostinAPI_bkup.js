var express = require('express');
var app = express();

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data
var AWS = require("aws-sdk");

app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded


app.use(express.static('public'));


app.post('/submitdata', function (req, res) {



console.log("******************************************");
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
			
			AWS.config.update({
			  region: "us-west-2",
			  endpoint: "http://localhost:8000",
			  accessKeyId: "fakeMyKeyId",
			  secretAccessKey: "fakeSecretAccessKey"
			});
			var dynamodb = new AWS.DynamoDB();
			var docClient = new AWS.DynamoDB.DocumentClient();
			
			var params = {
				TableName: 'Users',
				Key: { 
					'UserName': userid //(string | number | boolean | null | Binary)
				},
				AttributesToGet: [ 
					'UserName',
					'Client_ID',
					'Password',
				],
				ConsistentRead: true,
			};
            console.log("\n" + params)
			docClient.get(params, function(err, data, callback) {
                if (err) {
                    console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
                    
                } else {
                    console.log("GetItem succeeded:", JSON.stringify(data, null, 2));
                    
                    user_name = data.Item.UserName;
                    user_auth = data.Item.Password;
                    if (user_name == userid) {
                        msg = "\tFound User : " + user_name;
                        console.log(msg);
                        if (user_auth == authcode) {
                            msg = "\tValidated User.";
                            console.log(msg);
                        }
                        else {
                            msg = "\tInvalid Authorisation Code";
                            console.log(msg);
                            //res.sendStatus(401);
                        }
                    }


                }
                callback(err, data);
                console.log("Callback executed");

			});
			break;

		case "DB02":
			console.log("\nSending data packet to Amazon AWS");
			console.log(data);
			break;

		default:
			console.log("\n\nERROR : Unrecognised destination");
			res.sendStatus(400);
}
			

//console.log("MSG:"+msg)

console.log("\nIdentifying User....");


// Validate user id and auth code






	res.end();
})


var server = app.listen(8080, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Bostin CognIoT API listening at http:// %s :%s", host, port)

})

