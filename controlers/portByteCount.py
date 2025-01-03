import requests
import time

# Configuration
CONTROLLER_URL = "http://127.0.0.1:8080/stats/port/1"  # URL de l'API REST pour les stats du switch 1
POLL_INTERVAL = 2  # Intervalle en secondes entre les requêtes
PORTS_TO_MONITOR = [4, 5, 6]  # Liste des ports à surveiller

# Stocker les valeurs précédentes pour calculer les écarts
previous_stats = {port: {"rx_bytes": 0, "tx_bytes": 0} for port in PORTS_TO_MONITOR}

def get_port_stats():
    try:
        # Envoyer une requête GET pour obtenir les stats des ports
        response = requests.get(CONTROLLER_URL)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        stats = response.json()  # Convertir la réponse en JSON

        # Extraire les informations des ports spécifiques
        for stat in stats.get("1", []):  # "1" correspond à l'ID du switch
            port_no = stat["port_no"]
            if port_no in PORTS_TO_MONITOR:  # Vérifier si le port est surveillé
                rx_bytes = stat["rx_bytes"]
                tx_bytes = stat["tx_bytes"]

                # Calculer les écarts
                prev_rx = previous_stats[port_no]["rx_bytes"]
                prev_tx = previous_stats[port_no]["tx_bytes"]
                rx_diff = rx_bytes - prev_rx
                tx_diff = tx_bytes - prev_tx

                # Afficher les écarts
                print(f"Port {port_no} - Rx Diff: {rx_diff}, Tx Diff: {tx_diff}")

                # Mettre à jour les valeurs précédentes
                previous_stats[port_no]["rx_bytes"] = rx_bytes
                previous_stats[port_no]["tx_bytes"] = tx_bytes

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")

def main():
    print("Démarrage du contrôleur général...")
    while True:
        get_port_stats()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
