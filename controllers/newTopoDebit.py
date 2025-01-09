import requests
import time

# Adresse de l'API REST
api_url = "http://127.0.0.1:8080/stats/flow/1"

# Stockage des flux précédents pour calculer les différences de bytes
previous_flows = {}

# Fonction pour obtenir les statistiques des flux
def get_flow_stats():
    try:
        # Envoyer une requête GET pour obtenir les stats des flux du switch 1
        response = requests.get(api_url)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        stats = response.json()  # Convertir la réponse en JSON

        # Récupérer les flux du switch 1
        flows = stats.get("1", [])  # "1" correspond à l'ID du switch
        for flow in flows:
            in_port = flow["match"].get("in_port")
            # Filtrer pour les ports 1, 2, et 3
            if in_port in [2, 3, 4]:
                flow_id = (flow["priority"], str(flow["match"]))  # Identifiant unique du flux
                current_byte_count = flow["byte_count"]

                # Calculer l'écart si des données précédentes existent
                if flow_id in previous_flows:
                    byte_diff = current_byte_count - previous_flows[flow_id]
                    print(f"Port: {in_port}, Flow ID: {flow_id} - Byte Diff: {byte_diff}")
                else:
                    print(f"Port: {in_port}, Flow ID: {flow_id} - Initial Byte Count: {current_byte_count}")

                # Mettre à jour les valeurs précédentes
                previous_flows[flow_id] = current_byte_count

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête des flux : {e}")

# Boucle pour obtenir régulièrement les statistiques des flux
print("Starting periodic flow stats requests...")
while True:
    get_flow_stats()
    time.sleep(5)  # Intervalle entre les requêtes (en secondes)
