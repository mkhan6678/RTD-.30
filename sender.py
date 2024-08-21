import socket
import util

class Sender:

  def __init__(self):

        self.receiverAddressPort = ("127.0.0.1", 10346) # Student id 4181746

        # receiver buffer size
        self.bufferSize = 1016

        #receiver seq number
        self.rseqnum = 0

        #to keep track of packet count
        self.packetcount = 0

        #receiver ack number
        self.racknum = 0
        self.pktretransmit = False
        self.seq_num = 1
        self.ack_num = 0

        #create the UDP socket
        self.UDPSenderSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



  def rdt_send(self, app_msg_str):

      self.packetcount = self.packetcount + 1

      #if its not retransmitted packet chnage the seq no.
      if(not(self.pktretransmit)):   
          if(self.seq_num):
             self.seq_num = 0
          else:
              self.seq_num = 1          
      else:
          self.pktretransmit = False
      print("orginal message string: ", app_msg_str)
      self.pkt = util.make_packet(app_msg_str, self.ack_num, self.seq_num)

      print("packet created: ", self.pkt)

      #set the timeout for the socket timeout
      self.UDPSenderSocket.settimeout(4)

      #send the packet to receiver
      self.UDPSenderSocket.sendto(self.pkt, self.receiverAddressPort)
      
     
      print(f"packet num. {self.packetcount} is successfully sent to the receiver")

      #get the ack packet from receiver
      Sender.rtd_recv(self, app_msg_str)


  def rtd_recv(self,app_msg_str):
      try:

        self.msg_from_receiver ,addr = self.UDPSenderSocket.recvfrom(self.bufferSize)
        
        #get the sequence num in the received packet
        self.rseqnum = util.get_seq_num(self.msg_from_receiver)

        #get the ack num in the received packet
        self.racknum = util.is_ack(self.msg_from_receiver)

        # If packetcount is divisible by 3,then packet is corrupted
        if(self.seq_num == self.rseqnum):
            print(f"receiver acked the previous bit, resend!")
            print(f"\n[ACK-Previous retransmission]: {app_msg_str}")
            Sender.rdt_send(self, app_msg_str)
            self.pktretransmit = True

        else:
            print(f"packet is received correctly: seq. num {self.seq_num} = ACK num {self.racknum}. all done \n")

      except socket.error:
            # if packetnumber is divisible by 6, then timeout occcurs and packet will be resend
            print(f"receiver acked the previous bit, resend!")
            print(f"\n[timeout retransmission]: {app_msg_str}")
            self.pktretransmit = True
            Sender.rdt_send(self, app_msg_str)



