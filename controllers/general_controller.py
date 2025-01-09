import time
from monitor import start_monitoring_in_background, exceeded_ports, below_threshold_ports
import threading

def process_alerts(event):
    """
    Fonction pour traiter les alertes de dépassement du seuil et de retour sous le seuil.
    """
    while True:
        # Attendre qu'un événement soit déclenché
        event.wait()

        # Vérifier les ports qui ont dépassé le seuil
        if exceeded_ports:
            for port_no, avg_diff in exceeded_ports.items():
                print(f"ALERT: Port {port_no} exceeded the threshold with an average RX difference of {avg_diff:.2f} bytes.")

        # Vérifier les ports qui sont revenus sous le seuil
        if below_threshold_ports:
            for port_no, avg_diff in below_threshold_ports.items():
                print(f"ALERT: Port {port_no} is back below the threshold with an average RX difference of {avg_diff:.2f} bytes.")

        # Réinitialiser les dictionnaires après traitement
        exceeded_ports.clear()
        below_threshold_ports.clear()

        # Réinitialiser l'événement après traitement
        event.clear()

def main():
    CONTROLLER_URL = "http://127.0.0.1:8080/stats/port/1"
    PORTS_TO_MONITOR = [4]  
    THRESHOLD = 250  
    VERBOSE = True
    
    # Créer un objet Event pour communiquer entre threads
    event = threading.Event()

    # Démarrer la surveillance en arrière-plan 
    start_monitoring_in_background(CONTROLLER_URL, PORTS_TO_MONITOR, threshold=THRESHOLD, verbose=VERBOSE, event=event)

    # Démarrer un thread pour écouter les alertes
    threading.Thread(target=process_alerts, args=(event,), daemon=True).start()

    # Boucle principale qui peut effectuer d'autres actions
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
