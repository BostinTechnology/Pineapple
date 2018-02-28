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

describe('TEST API endpoint /authenticateuser', function() {
    // Unit test the authenticateuser functionality
    
    before(function() {
        // Stuff to do before the test runs
        AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
            var response = { "Item": {"Password" : "password"}};        // Data format response is ['Item']['Password'] = password
            callback(null, response);
        });
    });

    //users = ["m@mlb.com", "l@mlb.com", "c@mlb.com", "x@mlb.com"]
    //pwds = ["password", "pssaword", "passowrd", "psswoord"]
    //dbs = [ "FILE", "DBLocal", "DBRemote", "AWS", "other"]

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    it('should return a connected status for dblocal', function() {
        return chai.request(app)
        .get('/authenticateuser')
        .send({dest: 'DBLocal', id:'m@mlb.com', auth:'password'})
        .then(function(res) {
            expect(res).to.have.status(200);
        });
    });

    it('Should return connected status for dbremote', function() {
        return chai.request(app)
        .get('/authenticateuser')
        .send({dest: 'DBRemote', id:'m@mlb.com', auth:'password'})
        .then(function(res) {
            expect(res).to.have.status(200);
        });
    });
        
    it('Should return unknown error for file', function() {
        return chai.request(app)
        .get('/authenticateuser')
        .send({dest: 'FILE', id:'m@mlb.com', auth:'password'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });

    it('Should return unknown error for AWS', function() {
        return chai.request(app)
        .get('/authenticateuser')
        .send({dest: 'AWS', id:'m@mlb.com', auth:'password'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });

    it('Should return unknown error for an unknown source', function() {
        return chai.request(app)
        .get('/authenticateuser')
        .send({dest: 'other', id:'m@mlb.com', auth:'password'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });

});

describe('TEST API endpoint /authenticateuser, incorrect data structure', function() {
    // Unit test the authenticateuser functionality for multiple users

    var users = ["m@mlb.com", "l@mlb.com", "c@mlb.com", "x@mlb.com"]
    var pwds = ["password", "pssaword", "passowrd", "psswoord"]
    var dbs = [ "FILE", "DBLocal", "DBRemote", "AWS", "other"]

    // Try various database failure combinations, the first is a check it still works

    var tests = [
        // Correct data format response is ['Item']['Password'] = password
        {user: users[0], pwd: pwds[0], code: 200, resp: { "Item": {"Password" : pwds[0] }}},
        {user: users[0], pwd: pwds[1], code: 401, resp: { "Item": {"Password" : "" }}},
        {user: users[0], pwd: pwds[2], code: 401, resp: { "Item": ""} },
        {user: users[0], pwd: pwds[3], code: 401, resp: {}},

        
    ];

    after(function() {
        // stuff to do after the test has run
        AWS.restore('DynamoDB.DocumentClient');
    });

    for (var test of tests) {
        beforeEach(function() {
            // Stuff to do before the test runs
            AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
                var response = test.resp;        
                callback(null, response);
            });
        });


        it('should validate the correct user credentials for the various db connections', function() {
            console.log("[TEST] Combination:"+test.user+" :"+test.pwd+" :"+test.resp+" :"+test.code)
            return chai.request(app)
            .get('/authenticateuser')
            .send({dest: 'DBLocal', id: test.user, auth: test.pwd})
            .catch(err => err.response)
            .then(function(res) {
                expect(res).to.have.status(test.code);
            });
        });

    };
});


var users = ["m@mlb.com", "l@mlb.com", "c@mlb.com", "x@mlb.com"]
var pwds = ["password", "pssaword", "passowrd", "psswoord"]
var dbs = [ "FILE", "DBLocal", "DBRemote", "AWS", "other"]

// For each user, try all password combinations to check for pass / fail conditions

// loop through each user to check the various password combinations, checking that the right one passes

//   it('should validate the '+test.desc+' for the various db connections', function() {

var tests = [
    // for a given user try different passwords
    {desc: "correct user / password combination (DBLocal)", db: dbs[2],
        user: users[0], pwd: pwds[0], resp: { "Item": {"Password" : pwds[0]}}, code: 200},
    {desc: "correct user / incorrect password combination (DBLocal)", db: dbs[2],
        user: users[0], pwd: pwds[1], resp: { "Item": {"Password" : pwds[0]}}, code: 401},
    {desc: "correct user / incorrect password combination (DBRemote)", db: dbs[1],
        user: users[0], pwd: pwds[0], resp: { "Item": {"Password" : pwds[0]}}, code: 200},
    {desc: "correct user / incorrect password combination (DBRemote)", db: dbs[1],
        user: users[0], pwd: pwds[1], resp: { "Item": {"Password" : pwds[0]}}, code: 401},

    // repeat the above with a different user / password combination
    {desc: "different user / INCORRECT password combination (DBLocal)", db: dbs[2],
        user: users[1], pwd: pwds[0], resp: { "Item": {"Password" : pwds[1]}}, code: 401},
    {desc: "different user / password combination (DBLocal)", db: dbs[2],
        user: users[1], pwd: pwds[1], resp: { "Item": {"Password" : pwds[1]}}, code: 200},
    {desc: "different user / incorrect password combination (DBRemote)", db: dbs[1],
        user: users[1], pwd: pwds[0], resp: { "Item": {"Password" : pwds[1]}}, code: 401},
    {desc: "different user / incorrect password combination (DBRemote)", db: dbs[1],
        user: users[1], pwd: pwds[1], resp: { "Item": {"Password" : pwds[1]}}, code: 200},

    // try another user, but check it works with different db responses.
    {desc: "different user / different incorrect response combination (DBLocal)", db: dbs[2],
        user: users[2], pwd: pwds[2], resp: { "Item": {"Password" : pwds[0]}}, code: 401},
    {desc: "different user / different incorrect response combination (DBLocal)", db: dbs[2],
        user: users[2], pwd: pwds[2], resp: { "Item": {"Password" : pwds[2]}}, code: 200},
    {desc: "different user / different correct response combination (DBRemote)", db: dbs[1],
        user: users[2], pwd: pwds[2], resp: { "Item": {"Password" : pwds[2]}}, code: 200},
    {desc: "different user / different incorrect response combination (DBRemote)", db: dbs[1],
        user: users[2], pwd: pwds[2], resp: { "Item": {"Password" : pwds[3]}}, code: 401},


];

tests.forEach (function (test) {
    describe('TEST API endpoint /authenticateuser, user validation', function() {
        // Unit test the authenticateuser functionality for multiple users

        after(function() {
            // stuff to do after the test has run
            AWS.restore('DynamoDB.DocumentClient');
        });


        beforeEach(function() {
            // Stuff to do before the test runs
            AWS.mock('DynamoDB.DocumentClient', 'get', function (params, callback) {
                var response = test.resp;        // Data format response is ['Item']['Password'] = password
                callback(null, response);
            });
        });


        it('should validate the '+test.desc+' for the various db connections', function() {
            return chai.request(app)
            .get('/authenticateuser')
            .send({dest: test.db, id: test.user, auth: test.pwd})
            .catch(err => err.response)
            .then(function(res) {
                expect(res).to.have.status(test.code);
            });
        });

    });
});


