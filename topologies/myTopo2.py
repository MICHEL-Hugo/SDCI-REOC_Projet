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

    # Ajout du Datacenter
    dc1 = net.addDatacenter("dc1")

    # Ajout de l'API OpenStack
    api1 = OpenstackApiEndpoint("0.0.0.0", 6001)
    api1.connect_datacenter(dc1)
    api1.start()
    api1.connect_dc_network(net)

    # Ajout de l'API REST
    rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    rapi1.connectDCNetwork(net)
    rapi1.connectDatacenter(dc1)
    rapi1.start()

    # Ajout des composants
    srv = net.addDocker('srv', ip='10.0.0.4', dimage='host:server', dcmd="node server.js --local_ip '10.0.0.4' --local_port 8080 --local_name 'srv'")
    gi = net.addDocker('gi', ip='10.0.0.5', dimage='host:gateway', dcmd="node gateway.js --local_ip '10.0.0.5' --local_port 8282 --local_name 'gi' --remote_ip '10.0.0.4' --remote_port 8080 --remote_name 'srv'")

    # Gateways finales (directement reliées à gi)
    gf1 = net.addDocker('gf1', ip='10.0.0.7', dimage='host:gateway', dcmd="node gateway.js --local_ip '10.0.0.7' --local_port 8281 --local_name 'gf1' --remote_ip '10.0.0.5' --remote_port 8282 --remote_name 'gi'")
    gf2 = net.addDocker('gf2', ip='10.0.0.6', dimage='host:gateway', dcmd="node gateway.js --local_ip '10.0.0.6' --local_port 8281 --local_name 'gf2' --remote_ip '10.0.0.5' --remote_port 8282 --remote_name 'gi'")
    gf3 = net.addDocker('gf3', ip='10.0.0.8', dimage='host:gateway', dcmd="node gateway.js --local_ip '10.0.0.8' --local_port 8281 --local_name 'gf3' --remote_ip '10.0.0.5' --remote_port 8282 --remote_name 'gi'")

    # Périphériques finaux
    dev1 = net.addDocker('dev1', ip='10.0.0.1', dimage='host:device', dcmd="node device.js --local_ip '10.0.0.1' --local_port 9001 --local_name 'dev1' --remote_ip '10.0.0.7' --remote_port 8281 --remote_name 'gf1' --send_period 2000")
    dev2 = net.addDocker('dev2', ip='10.0.0.2', dimage='host:device', dcmd="node device.js --local_ip '10.0.0.2' --local_port 9001 --local_name 'dev2' --remote_ip '10.0.0.6' --remote_port 8281 --remote_name 'gf2' --send_period 2000")
    dev3 = net.addDocker('dev3', ip='10.0.0.3', dimage='host:device', dcmd="node device.js --local_ip '10.0.0.3' --local_port 9001 --local_name 'dev3' --remote_ip '10.0.0.8' --remote_port 8281 --remote_name 'gf3' --send_period 2000")

    # Création des liens directs (pas de switch)
    net.addLink(dc1, gi)
    net.addLink(gi, srv)
    net.addLink(gi, gf1)
    net.addLink(gi, gf2)
    net.addLink(gi, gf3)
    net.addLink(gf1, dev1)
    net.addLink(gf2, dev2)
    net.addLink(gf3, dev3)

    # Lancer le réseau
    net.start()
    net.CLI()
    net.stop()


def main():
    create_topology()


if __name__ == '__main__':
    main()
