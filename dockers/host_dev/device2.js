/**
 *  Author: Samir MEDJIAH medjiah@laas.fr
 *  Modified by Hugo MIHCEL
 *  File : device2.js
 *  Version : 0.1.0
 */

var express = require('express')
var app = express()
var request = require('request');

var argv = require('yargs').argv;
// --local_ip
// --local_port
// --local_name
// --remote_ip
// --remote_port
// --remote_name
// --normal_period
// --high_period
// --send_period

var LOCAL_ENDPOINT = {IP: argv.local_ip, PORT: argv.local_port, NAME: argv.local_name};
var REMOTE_ENDPOINT = {IP: argv.remote_ip, PORT: argv.remote_port, NAME: argv.remote_name};

// Configuration des périodes
var NORMAL_PERIOD = argv.normal_period; // Durée de la période normale en ms
var HIGH_PERIOD = argv.high_period;     // Durée de la période élevée en ms

// Intervalle entre envois (en ms)
var SEND_PERIOD = argv.send_period; // Intervalle fixe entre les envois

function doPOST(uri, body, onResponse) {
    request({method: 'POST', uri: uri, json: body}, onResponse);
}

function register() {
    doPOST(
        'http://' + REMOTE_ENDPOINT.IP + ':' + REMOTE_ENDPOINT.PORT + '/devices/register',
        {
            Name: LOCAL_ENDPOINT.NAME,
            PoC: 'http://' + LOCAL_ENDPOINT.IP + ':' + LOCAL_ENDPOINT.PORT,
        },
        function (error, response, respBody) {
            console.log(respBody);
        }
    );
}

// Gestion des données et des périodes
var dataItem = 0;
var isHighFlow = false;

function sendData() {
    let sendCount = isHighFlow ? 3 : 1; // Pendant HIGH_PERIOD, envoie 3 fois plus de données
    for (let i = 0; i < sendCount; i++) {
        doPOST(
            'http://' + REMOTE_ENDPOINT.IP + ':' + REMOTE_ENDPOINT.PORT + '/device/' + LOCAL_ENDPOINT.NAME + '/data',
            {
                Name: LOCAL_ENDPOINT.NAME,
                Data: dataItem++,
                CreationTime: Date.now(),
                ReceptionTime: null
            },
            function (error, response, respBody) {
                console.log(respBody);
            }
        );
    }
}

function alternatePeriods() {
    setTimeout(() => {
        isHighFlow = !isHighFlow;
        console.log(isHighFlow ? "Passage en mode HIGH_FLOW." : "Retour en mode NORMAL_FLOW.");
        alternatePeriods(); // Continuer l'alternance
    }, isHighFlow ? HIGH_PERIOD : NORMAL_PERIOD);
}

function startDataSending() {
    setInterval(sendData, SEND_PERIOD); // Lancer l'envoi des données à intervalle fixe
}

register();
startDataSending();
alternatePeriods(); // Lancer l'alternance des périodes
