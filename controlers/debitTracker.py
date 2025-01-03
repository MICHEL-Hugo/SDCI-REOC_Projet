import requests
import time

# Configuration
PORT_STATS_URL = "http://127.0.0.1:8080/stats/port/1"  # URL de l'API REST pour les stats des ports
FLOW_STATS_URL = "http://localhost:8080/stats/flow/1"  # URL de l'API REST pour les stats des flux
POLL_INTERVAL = 2  # Intervalle en secondes entre les requêtes
PORTS_TO_MONITOR = [4, 5, 6]  # Liste des ports à surveiller

# Stocker les valeurs précédentes pour calculer les écarts
previous_port_stats = {port: {"rx_bytes": 0, "tx_bytes": 0} for port in PORTS_TO_MONITOR}
previous_flows = {}

def get_port_stats():
    try:
        # Envoyer une requête GET pour obtenir les stats des ports
        response = requests.get(PORT_STATS_URL)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        stats = response.json()  # Convertir la réponse en JSON

        # Extraire les informations des ports spécifiques
        for stat in stats.get("1", []):  # "1" correspond à l'ID du switch
            port_no = stat["port_no"]
            if port_no in PORTS_TO_MONITOR:  # Vérifier si le port est surveillé
                rx_bytes = stat["rx_bytes"]
                tx_bytes = stat["tx_bytes"]

                # Calculer les écarts
                prev_rx = previous_port_stats[port_no]["rx_bytes"]
                prev_tx = previous_port_stats[port_no]["tx_bytes"]
                rx_diff = rx_bytes - prev_rx
                tx_diff = tx_bytes - prev_tx

                # Afficher les écarts
                print(f"Port {port_no} - Rx Diff: {rx_diff}, Tx Diff: {tx_diff}")

                # Mettre à jour les valeurs précédentes
                previous_port_stats[port_no]["rx_bytes"] = rx_bytes
                previous_port_stats[port_no]["tx_bytes"] = tx_bytes

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête des ports : {e}")

def get_flow_stats():
    try:
        # Envoyer une requête GET pour obtenir les stats des flux
        response = requests.get(FLOW_STATS_URL)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        stats = response.json()  # Convertir la réponse en JSON

        flows = stats.get("1", [])  # "1" correspond à l'ID du switch
        for flow in flows:
            # Identifier le flux via une combinaison unique de priorité et de match
            flow_id = (flow["priority"], str(flow["match"]))
            current_byte_count = flow["byte_count"]

            # Calculer l'écart si des données précédentes existent
            if flow_id in previous_flows:
                byte_diff = current_byte_count - previous_flows[flow_id]
                print(f"Flow {flow_id} - Byte Diff: {byte_diff}")
            else:
                print(f"Flow {flow_id} - Initial Byte Count: {current_byte_count}")

            # Mettre à jour les valeurs précédentes
            previous_flows[flow_id] = current_byte_count

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête des flux : {e}")

def main():
    print("Démarrage du contrôleur général (ports et flux)...")
    while True:
        get_port_stats()
        get_flow_stats()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
