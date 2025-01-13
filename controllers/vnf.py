import requests
import json

def create_vnf():
    url = "http://127.0.0.1:5001/restapi/compute/dc1/vnf"
    headers = {'Content-Type': 'application/json'}
    data = {
        "image": "vnf:gateway",
        "network": "(ip=10.0.0.60/24)"
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        try:
            response_json = response.json()
            mac_address = response_json['network'][0]['mac']
            print(f"Adresse MAC récupérée : {mac_address}")
            return mac_address
        except KeyError:
            print("Erreur : l'adresse MAC n'a pas été trouvée dans la réponse.")
    else:
        print(f"Erreur dans la création du VNF : {response.status_code}")
    return None

def redirect_dev2_traffic_to_vnf(mac_dst):
    url = "http://localhost:8080/stats/flowentry/add"
    headers = {'Content-Type': 'application/json'}
    data = {
        "dpid": 1,
        "priority": 1111,
        "match": {
            "in_port": 4,
            "nw_src": "10.0.0.11", 
            "nw_dst": "10.0.0.40",
            "dl_type": 2048
        },
        "actions": [
            {"type": "SET_FIELD", "field": "ipv4_dst", "value": "10.0.0.60"},
            {"type": "SET_FIELD", "field": "eth_dst", "value": mac_dst},
            {"type": "OUTPUT", "port": 1}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Règle de redirection dev2 <-> gi ajoutée avec succès.")
    else:
        print(f"Erreur lors de l'ajout de la règle : {response.status_code}")

def redirect_dev3_traffic_to_vnf(mac_dst):
    url = "http://localhost:8080/stats/flowentry/add"
    headers = {'Content-Type': 'application/json'}
    data = {
        "dpid": 1,
        "priority": 1111,
        "match": {
            "in_port": 5,
            "nw_src": "10.0.0.11", 
            "nw_dst": "10.0.0.40",
            "dl_type": 2048
        },
        "actions": [
            {"type": "SET_FIELD", "field": "ipv4_dst", "value": "10.0.0.60"},
            {"type": "SET_FIELD", "field": "eth_dst", "value": mac_dst},
            {"type": "OUTPUT", "port": 1}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Règle de redirection dev3 <-> gi ajoutée avec succès.")
    else:
        print(f"Erreur lors de l'ajout de la règle : {response.status_code}")

def redirect_vnf_to_gi():
    url = "http://localhost:8080/stats/flowentry/add"
    headers = {'Content-Type': 'application/json'}
    data = {
        "dpid": 1,
        "priority": 1111,
        "match": {
            "in_port": 1,
        },
        "actions": [
            {"type": "OUTPUT", "port": 2}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Règle de redirection ajoutée avec succès.")
    else:
        print(f"Erreur lors de l'ajout de la règle : {response.status_code}")

import requests

def delete_redirection():
    url = "http://localhost:8080/stats/flowentry/clear/1"
    response = requests.delete(url)
    if response.status_code == 200:
        print("Règle de redirection supprimée avec succès.")
    else:
        print(f"Erreur lors de la suppression des règles : {response.status_code}, {response.text}")

def main():
    """
    mac_address = create_vnf()
    if mac_address:
        redirect_dev2_traffic_to_vnf(mac_address)
        redirect_dev2_traffic_to_vnf(mac_address)
    redirect_vnf_to_gi()
    """

if __name__ == "__main__":
    main()
