import requests
import json
import argparse

def create_vnf():
    url = "http://127.0.0.1:5001/restapi/compute/dc1/vnf2"
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

def modify_request_vnf_to_new_gi(mac_dst):
    url = "http://localhost:8080/stats/flowentry/add"
    headers = {'Content-Type': 'application/json'}
    data = {
        "dpid": 1,
        "priority": 1111,
        "match": {
            "in_port": 3,
            "nw_src": "10.0.0.21", 
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
        print("Règle de redirection ajoutée avec succès.")
    else:
        print(f"Erreur lors de l'ajout de la règle : {response.status_code}")

def main():
    mac_address = create_vnf()
    if mac_address:
        modify_request_vnf_to_new_gi(mac_address)

if __name__ == "__main__":
    main()
