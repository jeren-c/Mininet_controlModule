import sys
import os

from pox.core import core

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_forest

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.addresses import IPAddr, EthAddr
import threading
import server
import time
from middle import form_data_queue

log = core.getLogger()

class Controller(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)
        
        self.FIREWALL_PRIORITY = 100
        self.PREMIUM_IP = 50
        
        self.table = {}
        self.fw = []
        self.state = []

        thread = threading.Thread(target=server.start_server)
        thread.start()

        thread = threading.Thread(target=self.process_form_data)
        thread.start()
            

    def process_form_data(self):
        while True:
            if form_data_queue:
                form_data = form_data_queue.get()
                for i in range(len(self.state)):
                    self.sendFirewallPolicy(self.state[i], form_data)
            time.sleep(1)

    def _handle_PacketIn (self, event):
        packet = event.parsed
        dpid = event.dpid
        src = packet.src
        dst = packet.dst
        inport = event.port     
        
        def install_enqueue(event, packet, outport, q_id):
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, inport)
            msg.data = event.ofp
            
            msg.actions.append(of.ofp_action_enqueue(port = outport, queue_id = q_id))
            event.connection.send(msg)

        def forward(message = None):
            if (dpid not in self.table) or (dst not in self.table[dpid]):
                flood()
            else:
                srcip = None
                if (packet.type == packet.IP_TYPE):
                    srcip = packet.payload.srcip                
                priority = 0             
                                 
                install_enqueue(event, packet, self.table[dpid][dst], priority)

        def flood (message = None):
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.in_port = inport
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))          
            event.connection.send(msg)
        
        self.table[dpid] = self.table.get(dpid, {})
        self.table[dpid][src] = inport
        forward()

    def sendFirewallPolicy(self, event, policy):
            src = policy[0] 
            dst = IPAddr(policy[1])
            outport = int(policy[2])
            msg = of.ofp_flow_mod()
            msg.match.dl_type=0x800
            msg.match.nw_dst=dst
            msg.match.nw_proto=6
            msg.match.tp_dst=outport           
            if src is not None:
                msg.match.nw_src = IPAddr(src)
            
            msg.priority = self.FIREWALL_PRIORITY
            event.connection.send(msg)            
            if src is None:
                src = "*"
        
    def _handle_ConnectionUp(self, event):
        dpid = dpid_to_str(event.dpid)
        self.state.append(event)      
        
        for i in self.fw:
            self.sendFirewallPolicy(event, i)
            
def launch():
    pox.openflow.discovery.launch()
    pox.openflow.spanning_forest.launch()
    core.registerNew(Controller)