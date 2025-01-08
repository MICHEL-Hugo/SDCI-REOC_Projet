import logging
from mininet.log import setLogLevel
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.openstack.openstack_api_endpoint import OpenstackApiEndpoint

logging.basicConfig(level=logging.INFO)
setLogLevel('info') # set Mininet loglevel
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

    # add OpenStack-like APIs to the emulated DC
    api1 = OpenstackApiEndpoint("0.0.0.0", 6001)
    api1.connect_datacenter(dc1)
    api1.start()
    api1.connect_dc_network(net)
    # add the command line interface endpoint to the emulated DC (REST API)
    rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    rapi1.connectDCNetwork(net)
    rapi1.connectDatacenter(dc1)
    rapi1.start()

    # Ajout des switchs
    s1 = net.addSwitch('s1', dpid='0000000000000001')
    s2 = net.addSwitch('s2', dpid='0000000000000002')
    sf1 = net.addSwitch('sf1', dpid='0000000000000003')
    sf2 = net.addSwitch('sf2', dpid='0000000000000004')
    sf3 = net.addSwitch('sf3', dpid='0000000000000005')

    # Ajout du serveur 
    srv = net.addDocker('srv', ip='10.0.0.50/24', dimage='host:server',dcmd="node server.js --local_ip '10.0.0.50' --local_port 8080 --local_name 'srv'")

    # Ajout de la Gateway Intermediaire
    gi = net.addDocker('gi', ip='10.0.0.40/24', dimage='host:gateway', dcmd="node gateway.js --local_ip '10.0.0.40' --local_port 8281 --local_name 'gi' --remote_ip '10.0.0.50' --remote_port 8080 --remote_name 'srv'")

    # Ajout des gateways finales comme hôtes, ce sont les réseaux de capteurs
    gf1 = net.addDocker('gf1', ip='10.0.0.10/24', dimage='host:gateway',dcmd="node gateway.js --local_ip '10.0.0.10' --local_port 8282 --local_name 'gf1' --remote_ip '10.0.0.40' --remote_port 8281  --remote_name 'gi'")  
    gf2 = net.addDocker('gf2', ip='10.0.0.20/24', dimage='host:gateway',dcmd="node gateway.js --local_ip '10.0.0.20' --local_port 8282 --local_name 'gf2' --remote_ip '10.0.0.40' --remote_port 8281  --remote_name 'gi'")
    gf3 = net.addDocker('gf3', ip='10.0.0.30/24', dimage='host:gateway',dcmd="node gateway.js --local_ip '10.0.0.30' --local_port 8282 --local_name 'gf3' --remote_ip '10.0.0.40' --remote_port 8281  --remote_name 'gi'")  

     # Ajout des hôtes finales, ce sont les réseaux de capteurs
    dev1 = net.addDocker('dev1', ip='10.0.0.11/24', dimage='host:highdevice',dcmd="node device2.js --local_ip '10.0.0.11' --local_port 9001 --local_name 'dev1' --remote_ip '10.0.0.10' --remote_port 8282 --remote_name 'gf1' --normal_period 10000 --high_period 10000 --send_period 2000")
    dev2 = net.addDocker('dev2', ip='10.0.0.21/24', dimage='host:device',dcmd="node device.js --local_ip '10.0.0.21' --local_port 9001  --local_name 'dev2' --remote_ip '10.0.0.20' --remote_port 8282 --remote_name 'gf2' --send_period 2000")
    dev3 = net.addDocker('dev3', ip='10.0.0.31/24', dimage='host:device',dcmd="node device.js --local_ip '10.0.0.31' --local_port 9001  --local_name 'dev3' --remote_ip '10.0.0.30' --remote_port 8282 --remote_name 'gf3' --send_period 2000")  




    # Ajout de l'app 
    #app = net.addDocker('app', ip='10.0.0.30', dimage='host:application',dcmd="node application.js --remote_ip '10.0.0.10' --remote_port 8080 --device_name 'dev1' --send_period 5000")
    #net.addLink(app, srv)

    # Création des liens
    net.addLink(dc1, s2)
    net.addLink(srv, s2)
    net.addLink(gi, s2)
    net.addLink(s2, s1)
    net.addLink(sf1, s1)
    net.addLink(sf2, s1)  
    net.addLink(sf3, s1)
    net.addLink(sf1, gf1)
    net.addLink(sf2, gf2)  
    net.addLink(sf3, gf3)
    net.addLink(sf1, dev1)
    net.addLink(sf2, dev2)
    net.addLink(sf3, dev3)    


    net.start()
    net.CLI()
    # when the user types exit in the CLI, we stop the emulator
    net.stop()

def main():
    create_topology()

if __name__ == '__main__':
    main()
