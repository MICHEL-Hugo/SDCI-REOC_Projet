import requests
import time

# Configuration
CONTROLLER_URL = "http://127.0.0.1:8080/stats/port/1"  # URL de l'API REST pour les stats du switch 1
POLL_INTERVAL = 0.5  # Intervalle en secondes entre les requêtes
PORTS_TO_MONITOR = [4,5,6]  # Liste des ports à surveiller

# Stocker les 4 dernières différences pour chaque port
last_diffs = {port: [] for port in PORTS_TO_MONITOR}

# Stocker les valeurs précédentes pour calculer les écarts
previous_stats = {port: 0 for port in PORTS_TO_MONITOR}

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

                # Calculer la différence avec la valeur précédente
                prev_rx = previous_stats[port_no]
                rx_diff = rx_bytes - prev_rx

                # Ajouter la différence aux dernières valeurs
                last_diffs[port_no].append(rx_diff)

                # Garder uniquement les 4 dernières valeurs
                if len(last_diffs[port_no]) > 4:
                    last_diffs[port_no].pop(0)

                # Calculer la moyenne des 4 dernières différences
                if len(last_diffs[port_no]) == 4:
                    avg_diff = sum(last_diffs[port_no]) / 4
                    print(f"Port {port_no} - Moyenne des dernières différences RX: {avg_diff:.2f} bytes")

                # Mettre à jour la valeur précédente
                previous_stats[port_no] = rx_bytes

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")

def main():
    print("Démarrage du contrôleur général...")
    while True:
        get_port_stats()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

