//
// Test module for BostinAPI_mb.js
//
// Initial version is to try and get some unit testing working
// based on
//    https://www.npmjs.com/package/aws-sdk-mock
//

/** TODO
 * Unable to test for the db not returning, no solution found so far
**/
"use strict";

var AWS = require('aws-sdk-mock');

const chai = require('chai');
const expect = require('chai').expect;

chai.use(require('chai-http'));

const app = require('../BostinAPI_mb.js');

//
// Test Routines
//

describe('TEST API endpoint /retrievedbversion', function() {
    // Test the retrieve db version functionality.
    // checks for good and bad responses
    
    before(function() {
        // Stuff to do before the test runs
        // Mock the user authentication - this has been validated elsewhere
        AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
            var response = { "Item": {"Password" : "password"}};      // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });

        // Mock the database response
        AWS.mock('DynamoDB.DocumentClient', 'query', function (params, callback) {
            var response = { "Items": {0 : {'version': "1.2"}}};        // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });
    });

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });


    // successful response with valid user - DBLocal
    it('should return a database version', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'m@mlb.com', auth:'password'})
        .then(function(res) {
            expect(res).to.have.status(200);
            console.log("[TEST] version received:" + res.text);
            expect(res.text).to.equal("1.2");
        });
    });

    // successful response, invalid user
    it('should return unauthorised to a database version', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'m@mlb.com', auth:'passwrd'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(401);
            expect(res.text).to.equal("Unauthorized");
        });
    });

    // More Database types, valid credentials
    // successful response with valid user - DBRemote
    it('should return a database version', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBRemote', id:'m@mlb.com', auth:'password'})
        .then(function(res) {
            expect(res).to.have.status(200);
            console.log("[TEST] version received:" + res.text);
            expect(res.text).to.equal("1.2");
        });
    });

    // successful response, invalid databse - FILE
    it('should return Not Implemented to a database version', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'FILE', id:'m@mlb.com', auth:'password'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
            expect(res.text).to.equal("Not Implemented");
        });
    });

    // successful response, invalid databse - AWS
    it('should return Not Implemented to a database version', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'AWS', id:'m@mlb.com', auth:'password'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
            expect(res.text).to.equal("Not Implemented");
        });
    });
    
    // successful response, invalid databse - unknown
    it('should return Not Implemented to a database version', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'other', id:'m@mlb.com', auth:'password'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
            expect(res.text).to.equal("Not Implemented");
        });
    });
});

describe('TEST API endpoint /retrievedbversion, empty version info', function() {
    // Test the retrieve db version functionality for when there are database issues.
    // checks for database errors / bad responses
    
    before(function() {
        // Stuff to do before the test runs
        // Mock the user authentication - this has been validated elsewhere
        AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
            var response = { "Item": {"Password" : "pssaword"}};      // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });

        // Mock the database response
        AWS.mock('DynamoDB.DocumentClient', 'query', function (params, callback) {
            var response = { "Items": {0 : {'version': ""}}};        // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });
    });

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    // successful response with valid user - DBLocal
    it('should return a database version of -1', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'l@mlb.com', auth:'pssaword'})
        .then(function(res) {
            expect(res).to.have.status(200);
            console.log("[TEST] version received:" + res.text);
            expect(res.text).to.equal("-1");
        });
    });

});

describe('TEST API endpoint /retrievedbversion, record zero', function() {
    // Test the retrieve db version functionality for when there are database issues.
    // checks for database errors / bad responses

    // no version record, should return 500 - internal server error
    
    before(function() {
        // Stuff to do before the test runs
        // Mock the user authentication - this has been validated elsewhere
        AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
            var response = { "Item": {"Password" : "pssaword"}};      // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });

        // Mock the database response
        AWS.mock('DynamoDB.DocumentClient', 'query', function (params, callback) {
            var response = { "Items": {0 : ""}};        // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });
    });

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    // successful response with valid user - DBLocal
    it('should return a database version of -1', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'l@mlb.com', auth:'pssaword'})
        .then(function(res) {
            expect(res).to.have.status(200);
            console.log("[TEST] version received:" + res.text);
            expect(res.text).to.equal("-1");
        });
    });

});

describe('TEST API endpoint /retrievedbversion, no version record', function() {
    // Test the retrieve db version functionality for when there are database issues.
    // checks for database errors / bad responses

    // no version record, should return 500 - internal server error
    
    before(function() {
        // Stuff to do before the test runs
        // Mock the user authentication - this has been validated elsewhere
        AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
            var response = { "Item": {"Password" : "pssaword"}};      // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });

        // Mock the database response
        AWS.mock('DynamoDB.DocumentClient', 'query', function (params, callback) {
            var response = { "Items": ""};        // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });
    });

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    // successful response with valid user - DBLocal
    it('should return a database version of -1', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'l@mlb.com', auth:'pssaword'})
        .then(function(res) {
            expect(res).to.have.status(200);
            console.log("[TEST] version received:" + res.text);
            expect(res.text).to.equal("-1");
        });
    });

});

describe('TEST API endpoint /retrievedbversion, empty response', function() {
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
            callback(null, "");
        });
    });

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    // successful response with valid user - DBLocal
    it('should return a database version of -1', function() {
        return chai.request(app)
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'l@mlb.com', auth:'pssaword'})
        .catch(err => err.response)
        .then(function(err) {
            expect(err).to.have.status(400);
        });
    });

});

describe('TEST API endpoint /retrievedbversion, error response from dynamodb', function() {
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
        .get('/retrievedbversion')
        .send({dest: 'DBLocal', id:'l@mlb.com', auth:'pssaword'})
        .catch(err => err.response)
        .then(function(err) {
            expect(err).to.have.status(400);
        });
    });

});



