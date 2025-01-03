import logging
from mininet.log import setLogLevel
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.openstack.openstack_api_endpoint import OpenstackApiEndpoint

logging.basicConfig(level=logging.INFO)
setLogLevel('info')  # set Mininet loglevel
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.base').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.compute').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.keystone').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.nova').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.neutron').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.heat').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.heat.parser').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.glance').setLevel(logging.DEBUG)
logging.getLogger('api.openstack.helper').setLevel(logging.DEBUG)

def create_topology():
    net = DCNetwork(monitor=False, enable_learning=True)

    dc1 = net.addDatacenter("dc1")  # DataCenter

    # Add OpenStack-like APIs to the emulated DC
    api1 = OpenstackApiEndpoint("0.0.0.0", 6001)
    api1.connect_datacenter(dc1)
    api1.start()
    api1.connect_dc_network(net)

    # Add the command line interface endpoint to the emulated DC (REST API)
    rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    rapi1.connectDCNetwork(net)
    rapi1.connectDatacenter(dc1)
    rapi1.start()

    # Ajout du serveur 
    srv = net.addDocker('srv', ip='10.0.0.10', dimage='host:server', dcmd="node server.js --local_ip '10.0.0.10' --local_port 8080 --local_name 'srv'")

    # Ajout de la Gateway Intermédiaire
    gi = net.addDocker('gi', ip='10.0.0.20', dimage='host:gateway', dcmd="node gateway.js --local_ip '10.0.0.20' --local_port 8282 --local_name 'gi' --remote_ip '10.0.0.10' --remote_port 8080 --remote_name 'srv'")

    # Ajout des hôtes finaux (les périphériques)
    dev1 = net.addDocker('dev1', ip='10.0.0.1', dimage='host:highdevice', dcmd="node device2.js --local_ip '10.0.0.1' --local_port 9001 --local_name 'dev1' --remote_ip '10.0.0.20' --remote_port 8282 --remote_name 'gi' --normal_period 10000 --high_period 10000 --send_period 2000")
    dev2 = net.addDocker('dev2', ip='10.0.0.2', dimage='host:device', dcmd="node device.js --local_ip '10.0.0.2' --local_port 9001  --local_name 'dev2' --remote_ip '10.0.0.20' --remote_port 8282 --remote_name 'gi' --send_period 4000")
    dev3 = net.addDocker('dev3', ip='10.0.0.3', dimage='host:device', dcmd="node device.js --local_ip '10.0.0.3' --local_port 9001  --local_name 'dev3' --remote_ip '10.0.0.20' --remote_port 8282 --remote_name 'gi' --send_period 6000")

    # Ajout du switch (réseau central)
    s1 = net.addSwitch('s1')

    # Liens entre les différents hôtes, la gateway intermédiaire et le serveur via le switch
    net.addLink(dc1, s1)
    net.addLink(srv, s1)
    net.addLink(gi, s1)
    net.addLink(dev1, s1)
    net.addLink(dev2, s1)
    net.addLink(dev3, s1)

    # Démarrer le réseau et l'interface de commande
    net.start()
    net.CLI()
    
    # Lorsque l'utilisateur tape 'exit' dans l'interface CLI, arrêter l'émulateur
    net.stop()

def main():
    create_topology()

if __name__ == '__main__':
    main()
