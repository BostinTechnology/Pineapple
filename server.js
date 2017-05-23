var express = require('express');
var app = express();

var bodyParser = require('body-parser');
var multer = require('multer'); // v1.0.5
var upload = multer(); // for parsing multipart/form-data

app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded


app.use(express.static('public'));

app.get('/index.html', function (req, res) {
   res.sendFile( __dirname + "/" + "getName.html" );
})

app.get('/login.html', function (req, res) {
   res.sendFile( __dirname + "/" + "login.html" );
})

app.get('/process_get', function (req, res) {
   // Prepare output in JSON format
   response = {
      first_name:req.query.first_name,
      last_name:req.query.last_name
   };
   console.log(response);
   res.end(JSON.stringify(response));
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


var server = app.listen(8000, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Example app listening at http:// %s :%s", host, port)

})
