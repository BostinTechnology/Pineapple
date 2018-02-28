//
// Test module for BostinAPI_mb.js
//
// Initial version is to try and get some unit testing working
// based on
//    https://www.npmjs.com/package/aws-sdk-mock
//


// TODO: Need to add response code 400 for when AWS doesn't respond

"use strict";

var AWS = require('aws-sdk-mock');

const chai = require('chai');
const expect = require('chai').expect;

chai.use(require('chai-http'));

const app = require('../BostinAPI_mb.js');

//
// Test Routines
//

describe('TEST API endpoint /connected', function() {

    before(function() {
        // Stuff to do before the test runs
    });

    after(function() {
        // stuff to do after the test has run
    });

    it('should return a connected status for dblocal', function() {
        return chai.request(app)
        .get('/connected')
        .send({dest: 'DBLocal'})
        .then(function(res) {
            expect(res).to.have.status(200);
        });
    });
    
    it('should return a connected status for dbremote', function() {
        return chai.request(app)
        .get('/connected')
        .send({dest: 'DBRemote'})
        .then(function(res) {
            expect(res).to.have.status(200);
        });
    });
    
    it('should return a failed status for FILE', function() {
        return chai.request(app)
        .get('/connected')
        .send({dest: 'FILE'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });
    
    it('should return a failed status for AWS', function() {
        return chai.request(app)
        .get('/connected')
        .send({dest: 'AWS'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });
    
    it('should return a failed status for anything else', function() {
        return chai.request(app)
        .get('/connected')
        .send({dest: 'Test'})
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });
    
    it('should return a failed status for no database', function() {
        return chai.request(app)
        .get('/connected')
        .catch(err => err.response)
        .then(function(res) {
            expect(res).to.have.status(501);
        });
    });
});
