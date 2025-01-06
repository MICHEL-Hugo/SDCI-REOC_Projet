const express = require('express');
const bodyParser = require('body-parser');
const Queue = require('fifo');
const request = require('request');

const app = express();
const port = 9090; // Port d'écoute du proxy

// Paramètres de régulation
const outputRate = 800;  // Débit de sortie (octets par seconde)
const fifoCacheSize = 10240; // Taille du cache FIFO (en octets)

// Cache FIFO pour stocker les données
const fifoCache = new Queue();

// Parse les corps des requêtes en JSON
app.use(bodyParser.json());

// Configuration des endpoints
const REMOTE_ENDPOINT = {
    IP: '10.0.0.20',  // Remplacer par l'adresse IP du destinataire
    PORT: 8282,       // Remplacer par le port du destinataire
};

// Fonction pour rediriger les données vers le destinataire
function sendData(data) {
    request.post(
        {
            url: `http://${REMOTE_ENDPOINT.IP}:${REMOTE_ENDPOINT.PORT}/device/data`,  // L'URL du destinataire
            json: data,
        },
        function (error, response, body) {
            if (error) {
                console.error('Erreur lors de l\'envoi des données :', error);
            } else {
                console.log('Données envoyées avec succès:', body);
            }
        }
    );
}

// Fonction pour réguler la vitesse d'envoi des données
function regulateSpeed() {
    if (fifoCache.size > 0) {
        const data = fifoCache.shift();
        // Envoi des données vers le destinataire
        sendData(data);
    }
}

// Route pour recevoir des données envoyées par les dispositifs
app.post('/data', (req, res) => {
    const data = req.body;

    // Si le cache est plein, on enlève les anciennes données
    if (fifoCache.size >= fifoCacheSize) {
        console.log('Cache plein, suppression des données anciennes');
        fifoCache.shift();  // On enlève la première donnée
    }

    // Ajout des données reçues dans le cache FIFO
    fifoCache.push(data);
    console.log('Données reçues et ajoutées au cache FIFO:', data);

    res.status(200).send('Données reçues et ajoutées au cache');
});

// Fonction pour envoyer les données à intervalle régulier
setInterval(() => {
    regulateSpeed();  // Réguler et envoyer les données en fonction du débit
}, 1000 / outputRate);  // Débit de sortie (envois par seconde)

// Démarrage du serveur
app.listen(port, () => {
    console.log(`Proxy VNF en écoute sur le port ${port}`);
});
