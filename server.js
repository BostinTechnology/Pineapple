var express = require('express');
var app = express();

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data

app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded


app.use(express.static('public'));


app.get('/process_get', function (req, res) {
   // Prepare output in JSON format
   response = {
      first_name:req.query.first_name,
      last_name:req.query.last_name
   };
   console.log(response);
   res.end(JSON.stringify(response));
})

app.get('/response', function (req, res) {
   // Prepare output in JSON format
   response = {
      rescode:req.query.rescode
    };
	console.log(response);
	var rc = req.query.rescode;
	res.status(rc).end();

})

app.get('/validate', function (req, res) {
   // Prepare output in JSON format
   response = {
      id:req.query.id,
      auth:req.query.auth
   };
   console.log(response);
   res.end(JSON.stringify(response));
})

app.post('/validate', function (req, res) {
   // Prepare output in JSON format
	console.log("Received....");
	console.log(req.body);
	response = {
		user_id:req.body.id,
		user_auth:req.body.auth
	};
	console.log("Understood as :-" );
	
	console.log(response);
	console.log("+++++++++++++++++++++++++");
	
	res.end("Logged in");



})

app.post('/submitdata', function (req, res) {

console.log("******************************************");
console.log("POST message received as follows: -");

console.log(req.body);
console.log("\nIdentifying User....");

var userid, authcode, dest, datapacket;

// Temporary, this is the list of authorised users.
var auth_users = '{ "Users" : [' +
'{ "id":"Ciaran" , "auth":"qwerty" },' +
'{ "id":"M0XTD" , "auth":"IO92eg" },' +
'{ "id":"Matthew" , "auth":"CognIoT" } ]}';

 
userid = req.body.id;
authcode = req.body.auth;
dest = req.body.dest;
data = req.body.data;

obj = JSON.parse(auth_users);

// Validate user id and auth code

for (i in obj.Users) {
	user_name = obj.Users[i].id;
	user_auth = obj.Users[i].auth;
	if (user_name == userid) {
		msg = "\tFound User : " + user_name;
		console.log(msg);
		if (user_auth == authcode) {
			msg = "\tValidated User."
			console.log(msg);
		}
		else {
			msg = "\tInvalid Authorisation Code";
			console.log(msg);
			res.status(401).end();
		}
	}
}


// With valid user, identify destination
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
			console.log(data);
			break;

		case "DB01":
			console.log("\nSending data packet to Amazon AWS");
			console.log(data);
			break;

		default:
			console.log("\n\nERROR : Unrecognised destination");
			res.sendStatus(400);
}
			



	res.end();
})






var server = app.listen(8000, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Example app listening at http:// %s :%s", host, port)

})
