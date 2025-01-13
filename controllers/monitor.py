import requests
import time
import socket
import json

RYU_REST_API_URL = "http://localhost:8080"  # URL de l'API REST de Ryu
SWITCH_ID = "1"  # ID du switch à surveiller
THRESHOLD = 900  # Seuil en bytes pour déterminer si le trafic est élevé ou bas

# Configuration du socket pour communiquer avec un autre script
HOST = "127.0.0.1"  # Adresse IP locale
PORT = 65432  # Port d'écoute pour les messages

def get_switch_stats(switch_id, port_id):
    """Obtenez les statistiques d'un port spécifique du switch depuis l'API REST de Ryu"""
    url = f"{RYU_REST_API_URL}/stats/port/{switch_id}/{port_id}"
    try:
        response = requests.get(url, timeout=10)  # Augmenter le délai d'attente à 10 secondes
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des statistiques du port {port_id} du switch {switch_id}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à l'API REST de Ryu: {e}")
    return None

def monitor_traffic():
    """Surveille les statistiques des ports du switch et envoie des messages"""
    last_rx_bytes = {1: 0, 3: 0, 4: 0, 5: 0}  # Stocke les dernières valeurs de rx_bytes pour chaque port
    last_tx_bytes = {2: 0}  # Stocke la dernière valeur de tx_bytes pour le port 1

    # Configuration du socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"En attente de connexion sur {HOST}:{PORT}...")
        conn, addr = s.accept()
        print(f"Connexion acceptée depuis {addr}")

        with conn:
            while True:
                status = {}

                # Surveiller rx_bytes pour les ports 3, 4 et 5
                for port in [1, 3, 4, 5]:
                    stats = get_switch_stats(SWITCH_ID, port)
                    if stats:
                        rx_bytes = stats.get(str(SWITCH_ID), [{}])[0].get('rx_bytes', None)

                        if rx_bytes is not None:
                            # Calcul de la différence
                            diff_rx_bytes = rx_bytes - last_rx_bytes[port]
                            print(f"Port {port} - rx_bytes instantanés : {diff_rx_bytes}")

                            # Mise à jour de la dernière valeur
                            last_rx_bytes[port] = rx_bytes

                            # Vérification par rapport au seuil
                            if diff_rx_bytes > THRESHOLD:
                                status[f"port_{port}_rx"] = "above"
                            else:
                                status[f"port_{port}_rx"] = "below"
                        else:
                            print(f"Impossible de récupérer rx_bytes pour le port {port} du switch {SWITCH_ID}")
                    else:
                        print(f"Impossible de récupérer les statistiques pour le port {port} du switch {SWITCH_ID}")

                # Surveiller tx_bytes pour le port 1
                port = 2
                stats = get_switch_stats(SWITCH_ID, port)
                if stats:
                    tx_bytes = stats.get(str(SWITCH_ID), [{}])[0].get('tx_bytes', None)

                    if tx_bytes is not None:
                        # Calcul de la différence
                        diff_tx_bytes = tx_bytes - last_tx_bytes[port]
                        print(f"Port {port} - tx_bytes instantanés : {diff_tx_bytes}")

                        # Mise à jour de la dernière valeur
                        last_tx_bytes[port] = tx_bytes

                        # Enregistrer la valeur actuelle de tx_bytes
                        status[f"port_{port}_tx"] = tx_bytes
                    else:
                        print(f"Impossible de récupérer tx_bytes pour le port {port} du switch {SWITCH_ID}")
                else:
                    print(f"Impossible de récupérer les statistiques pour le port {port} du switch {SWITCH_ID}")

                # Envoi des résultats sous forme de JSON
                message = json.dumps(status)
                conn.sendall(message.encode("utf-8"))

                # Pause avant la prochaine surveillance
                time.sleep(2)

def main():
    monitor_traffic()

if __name__ == '__main__':
    main()
