import requests
import time
import threading

# Dictionnaires pour suivre l'état des ports
exceeded_ports = {}  # Ports qui ont dépassé le seuil
below_threshold_ports = {}  # Ports qui sont revenus en dessous du seuil

def monitor_port(stats_url, port_to_monitor, poll_interval=0.5, threshold=200, verbose=True, event=None):
    """
    Fonction qui surveille les ports en arrière-plan et envoie des alertes si la moyenne dépasse le seuil
    ou si elle retombe en dessous du seuil.
    
    :param stats_url: URL de l'API des statistiques du switch
    :param port_to_monitor: Liste des ports à surveiller
    :param poll_interval: Intervalle entre chaque vérification (en secondes)
    :param threshold: Seuil au-delà duquel une alerte est générée
    :param verbose: Si True, affiche les informations détaillées
    :param event: L'événement à signaler lorsqu'un changement de seuil se produit
    """
    last_diffs = {port: [] for port in port_to_monitor}
    previous_stats = {port: 0 for port in port_to_monitor}

    while True:
        try:
            # Envoyer une requête GET pour obtenir les stats des ports
            response = requests.get(stats_url)
            response.raise_for_status()  # Lève une exception pour les erreurs HTTP
            stats = response.json()  # Convertir la réponse en JSON

            # Extraire les informations des ports spécifiques
            for stat in stats.get("1", []):  # "1" correspond à l'ID du switch
                port_no = stat["port_no"]
                if port_no in port_to_monitor:
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

                        # Vérifier si la valeur dépasse le seuil
                        if avg_diff > threshold:
                            if port_no not in exceeded_ports:
                                #print(f"ALERT: Port {port_no} exceeded the threshold with an average RX difference of {avg_diff:.2f} bytes.")
                                exceeded_ports[port_no] = avg_diff  # Marquer comme ayant dépassé le seuil
                                if event:
                                    event.set()  # Déclencher un événement de dépassement
                        else:
                            if port_no in exceeded_ports:
                                #print(f"ALERT: Port {port_no} is back below the threshold with an average RX difference of {avg_diff:.2f} bytes.")
                                below_threshold_ports[port_no] = avg_diff  # Marquer comme revenu sous le seuil
                                del exceeded_ports[port_no]  # Supprimer du dictionnaire des ports ayant dépassé le seuil
                                if event:
                                    event.set()  # Déclencher un événement de retour sous le seuil

                        # Afficher des informations détaillées si demandé (verbose)
                        if verbose:
                            print(f"Port {port_no} - Average RX difference of last 4 readings: {avg_diff:.2f} bytes")

                    # Mettre à jour la valeur précédente
                    previous_stats[port_no] = rx_bytes

        except requests.exceptions.RequestException as e:
            print(f"Error during the request: {e}")

        # Attendre avant de recommencer l'itération
        time.sleep(poll_interval)

def start_monitoring_in_background(stats_url, port_to_monitor, threshold=200, verbose=True, event=None):
    """
    Fonction pour démarrer la surveillance en arrière-plan dans un thread séparé.
    """
    monitoring_thread = threading.Thread(target=monitor_port, args=(stats_url, port_to_monitor, 0.5, threshold, verbose, event))
    monitoring_thread.daemon = True  # Le thread sera fermé quand le programme principal termine
    monitoring_thread.start()
    
    print(f"Monitoring started in the background with threshold {threshold}.")
