# This file is part of POX controller.


# These next two imports are common POX convention
from pox.core import core
from pox.lib.util import dpidToStr
from collections import defaultdict
import pox.openflow.libopenflow_01 as of
import pox.openflow.spanning_tree as spanning_tree
import pox.openflow.discovery as discovery
import pox.lib.packet as pack
import time

# include as part of the betta branch
from pox.openflow.of_json import *

# alogger is created to log the events.
log = core.getLogger()


# portmap table maps port for every link between switches
# flowtable table stores next hop for packet transmission between given switches 
portmap ={}
flowtable={}
switches = set()
table={}
tree={}

#This method activates all physical links between switches and
# adds corresponding flows in switches using ofp_flow_mod()
def test_flow_add():
  log.debug("Links only flow config activating")
  for conn in core.openflow.connections:
    conn_id =conn.dpid

    for s1 in switches:

      if s1 == conn_id:
        sw_id_str = dpidToStr(conn_id)
        length =len(sw_id_str)
        sw_id = sw_id_str[length-1]
        host_ip_src = IPAddr("10.0.0."+sw_id);

        for s2 in switches:
          if s1!=s2:
            if (s1,s2) in portmap:
              out_port = portmap[(s1,s2)]
              sw2_id_str = dpidToStr(s2)
              len2 = len(sw2_id_str)
              sw2_id = sw2_id_str[len2-1]

              host_ip_dst = IPAddr("10.0.0."+sw2_id_str)

              msg = of.ofp_flow_mod()
              msg.match.nw_dst = host_ip_dst
              msg.hard_timeout = 150
              msg.actions.append(of.ofp_action_output(port = portmap[(s1,s2)]))
              conn.send(msg)
  log.debug("Links only flow config activated")          

#This method parses paths.file, which contains links that are active
#After parsing, links are stored in flowtable table. This table is used to add flows in switches later. 
def populate_flow_table():
  log.debug("Reading paths file")
  f = open('paths.file','r')
  for line in f:
    currentline = line
    x_list = currentline.split('->')
    flowtable[(x_list[0],x_list[2])] = x_list[1].rstrip()

#This method is called when a link is created between switch
def _handle_links (event):
  """
  Handle link events and add or update port mapping table
  
  """

  for l in core.openflow_discovery.adjacency:
    sw_id1 = dpidToStr(l.dpid1)
    len_sw1 = len(sw_id1)
    sw1 = sw_id1[len_sw1-1]
    sw_id2 = dpidToStr(l.dpid2)
    len_sw2 = len(sw_id2)
    sw2 = sw_id2[len_sw2-1]
    if (sw1,sw2) not in portmap:
      portmap[(sw1,sw2)]=l.port1
      portmap[(sw2,sw1)]=l.port2
      if sw1 not in switches:
        log.debug("Adding switch to database: %s",(dpidToStr(l.dpid1)))
        switches.add(sw1)
      if sw2 not in switches:
        log.debug("Adding switch to database: %s",(dpidToStr(l.dpid2)))
        switches.add(sw2)
      log.debug("link between %s:%s to %s:%s ",dpidToStr(l.dpid1),l.port1,dpidToStr(l.dpid2),l.port2)

# This method is called periodically by timer
def _flow_func ():
  log.debug("Timer function started")
  test_flow_add()
  time.sleep(120)
  populate_flow_table()

def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
  log.debug("Sent %i flow stats request", len(core.openflow._connections))

def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("FlowStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)

#This method is called when a packet is received from switch
def _handle_PacketIn (event):
  """
  Handle messages the switch has sent us because it has no
  matching rule.
  """

  def drop ():
    # Kill buffer on switch
    if event.ofp.buffer_id is not None:
      msg = of.ofp_packet_out()
      msg.buffer_id = event.ofp.buffer_id
      msg.in_port = event.port
      event.connection.send(msg)

  packet = event.parsed
  packet_in= event.ofp
  match = of.ofp_match.from_packet(packet)
  
  if ( match.dl_type == packet.ARP_TYPE ):
    r = pack.arp()
    r.opcode = pack.arp.REPLY
    r.hwdst = match.dl_src
    r.protosrc = match.nw_dst
    r.protodst = match.nw_src

    ip = str(match.nw_dst)
    last = ip[-1]

    r.hwsrc = EthAddr("00:00:00:00:00:0"+last)
    e = ethernet(type=packet.ARP_TYPE, src=r.hwsrc, dst=r.hwdst)
    e.set_payload(r)
    #log.debug("%i %i answering ARP for %s" %
     #( event.dpid, event.port,
      # str(r.protosrc)))
    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port =
                                          of.OFPP_IN_PORT))
    msg.in_port = event.port
    event.connection.send(msg)
  else:
    if packet.type == packet.LLDP_TYPE:
      return drop()
    cur = dpidToStr(event.connection.dpid)
    cur_sw = cur[len(cur)-1]
    
    if packet.src == EthAddr("00:00:00:00:00:0"+cur_sw):
      msg = of.ofp_flow_mod()
      msg.match.dl_dst = packet.src
      msg.actions.append(of.ofp_action_output(port = event.port))
      event.connection.send(msg)

    """
    if packet.dst == EthAddr("ff:ff:ff:ff:ff:ff"):
      msg = of.ofp_packet_out()
      msg.data = packet_in
      msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))  
      event.connection.send(msg)
    else:
    """
    if not packet.dst.is_multicast:
      dst_ip = str(match.nw_dst)
      dst_sw = dst_ip[len(dst_ip)-1] 
      #log.debug("Packet dest : %s",(match.nw_dst))
      if dst_sw in switches:
        if cur_sw==dst_sw:
          #log.debug("current switch is destination switch: %s",(cur_sw))
          
          msg = of.ofp_packet_out()
          msg.data = packet_in
          msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
          event.connection.send(msg)      
          """
          msg = of.ofp_flow_mod()
          msg.match.dl_dst = packet.src
          msg.actions.append(of.ofp_action_output(port = ))
          event.connection.send(msg)
          """
        else:
          next_sw = flowtable[(cur_sw,dst_sw)]   
          #host_ip_dst = IPAddr("10.0.0."+dst_sw)
          msg = of.ofp_flow_mod()
          #msg.match.nw_dst = host_ip_dst
          msg.match.dl_src = packet.src
          msg.match.dl_dst = packet.dst
          msg.hard_timeout = 300
          msg.data = event.ofp
          msg.actions.append(of.ofp_action_output(port = portmap[(cur_sw,next_sw)]))
          event.connection.send(msg)

#This method is called when this python file is executed
def launch ():
  from pox.lib.recoco import Timer
  def start ():
    populate_flow_table()
    core.openflow_discovery.addListenerByName("LinkEvent", _handle_links)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn) 
    #core.openflow.addListenerByName("FlowStatsReceived", 
    #_handle_flowstats_received)
   #log.info("FlowVisor Pair-Learning switch running.")
  
  
  #Timer(100, _timer_func, recurring=True) 
  Timer(300, _flow_func, recurring=True)
   
  core.call_when_ready(start, "openflow_discovery")
