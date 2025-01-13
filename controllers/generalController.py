import socket
import subprocess
import time
import json
from requests import RequestException
from vnf import create_vnf, redirect_dev2_traffic_to_vnf, redirect_dev3_traffic_to_vnf, redirect_vnf_to_gi, delete_redirection


HOST = "127.0.0.1"  # Adresse IP du serveur
PORT = 65432  # Port d'écoute du serveur
MONITOR_SCRIPT = "monitor.py"  # Nom du script à démarrer

# Variables globales pour suivre l'état précédent du port 3
previous_port3_status = "above"

def start_monitor_script():
    """Démarre le script monitor.py en arrière-plan"""
    try:
        print(f"Démarrage de {MONITOR_SCRIPT}...")
        subprocess.Popen(["python3", MONITOR_SCRIPT])  # Utilisez "python" si vous êtes sur Windows
        print(f"{MONITOR_SCRIPT} démarré.")
    except Exception as e:
        print(f"Erreur lors du démarrage de {MONITOR_SCRIPT} : {e}")

def redirect_ports(mac_address):
    """Action à effectuer lorsque le port 3 dépasse le seuil"""
    print("Configuration des redirections...")
    try:
        redirect_dev2_traffic_to_vnf(mac_address)
        redirect_dev3_traffic_to_vnf(mac_address)
        redirect_vnf_to_gi()
    except RequestException as e:
        print(f"Erreur lors de la configuration des redirections : {e}")

def restore_topology():
    """Action à effectuer lorsque le port 3 revient sous le seuil"""
    print("Restauration de la topologie initiale...")
    try:
        delete_redirection()
    except RequestException as e:
        print(f"Erreur lors de la restauration de la topologie : {e}")

def handle_port3_status(current_status, mac_address):
    """Gère les changements d'état pour le port 3"""
    global previous_port3_status

    if current_status == "above" and previous_port3_status == "below":
        # Si le port 3 passe en dépassement
        redirect_ports(mac_address)
    elif current_status == "below" and previous_port3_status == "above":
        # Si le port 3 revient sous le seuil
        restore_topology()

    # Mettre à jour l'état précédent
    previous_port3_status = current_status

def receive_messages(mac_address):
    """Se connecte au serveur et reçoit les messages"""
    # Attendre que le serveur de monitor.py soit prêt
    time.sleep(2)  # Donne le temps au script monitor.py de démarrer et configurer le socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connexion à {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connecté au serveur.")

        while True:
            data = s.recv(1024)
            if not data:
                break

            # Décoder le message JSON reçu
            message = data.decode("utf-8")
            print(f"Message reçu : {message}")

            # Convertir le message en dictionnaire Python
            port_status = json.loads(message)

            # Vérifier l'état du port 3
            handle_port3_status(port_status.get('port_3_rx'), mac_address)

if __name__ == "__main__":
    start_monitor_script()
    mac_address = create_vnf()
    receive_messages(mac_address)