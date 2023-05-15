import os
import sys
import atexit
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections 

net = None
linkbw = {}
class TreeTopo(Topo):		
    def __init__(self):
            Topo.__init__(self)
    
    def getContents(self, contents):
        hosts = contents[0]
        switch = contents[1]
        links = contents[2]
        linksInfo = contents[3:]
        return hosts, switch, links, linksInfo

    def build(self):
        f = open('./topology.in',"r")
        contents = f.read().split()
        host, switch, link, linksInfo = self.getContents(contents)
        print("Hosts: " + host)
        print("switch: " + switch)
        print("links: " + link)
        print("linksInfo: " + str(linksInfo))
        for x in range(1, int(switch) + 1):
            sconfig = {'dpid': "%016x" % x}
            self.addSwitch('s%d' % x, **sconfig)
        for y in range(1, int(host) + 1):
            ip = '10.0.0.%d/8' % y
            self.addHost('h%d' % y, ip=ip)
        for x in range(int(link)):
            info = linksInfo[x].split(',')
            host = info[0]
            switch = info[1]
            bandwidth = int(info[2])
            self.addLink(host, switch)
            linkbw[(host, switch)] = bandwidth

def startNetwork():
    info('** Creating the tree network\n')
    topo = TreeTopo()
    controllerIP = '0.0.0.0'
    global net
    net = Mininet(topo=topo, link = TCLink,
                  controller=lambda name: RemoteController(name, ip=controllerIP),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
    net.start()    
    info('** Running CLI\n')
    CLI(net)

def stopNetwork():
    if net is not None:
        dumpNodeConnections(net.hosts)
        net.stop()
        os.system('sudo ovs-vsctl --all destroy Qos')
        os.system('sudo ovs-vsctl --all destroy Queue')

if __name__ == '__main__':
    atexit.register(stopNetwork)

    setLogLevel('info')
    startNetwork()
