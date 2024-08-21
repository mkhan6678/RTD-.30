import socket
import time
import util

recev_addr = ("127.0.0.1", 10346) #Student Id = 4181746

#buffer size for receiver
bufferSize = 1016

# Creating a UDP socket
UDPReceiverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPReceiverSocket.bind(recev_addr) 

seq_num = 1
pkt_number = 1


while(True):

    #receive the sender data
    pkt, address = UDPReceiverSocket.recvfrom(bufferSize)

    print(f"\nPacket number {pkt_number} recieved : {pkt}")
    
    verifychecksumpkt = util.verify_checksum(pkt)
 
    HEADERSIZE = 12  # Headersize
    msg = b''
    # Get only the data and remove the header 
    for byte in pkt:        
        HEADERSIZE -= 1
        if(HEADERSIZE < 0):
            msg = msg + byte.to_bytes(1, 'big')
    data = str(msg, 'utf-8')

    # Get the seq no of received packet
    seq_num = util.get_seq_num(pkt)
       
   
    #Simulating packet loss   
    if(pkt_number%6 == 0):
            print("simulating packet loss: sleep a while to trigger timeout event on the sender side... all done for this packet!")  
            time.sleep(7)

     #Simulating packet bit errors/corrupted
    elif(pkt_number%3 == 0):
            print("simulating packet bit errors/corrupted: ACK the previous packet! \n all done for this packet!")

            # Acknowledge with prior sequence number
            if(seq_num):
                seq_num = 0
            else:
                seq_num = 1
    
     # Validation of packet
    elif(verifychecksumpkt):
            print(f"packet is expected, message string delivered: {data} \npacket is delivered, now creating and sending the ACK packet....\n all done for this packet!")
            
    #With acknowledge bit set to 1, acknowledge each packet
    ack_num = 1

      #create the packet with ack and seq bit set
    ack_pkt = util.make_packet(data, ack_num, seq_num)
    
     # Replying to sender

    UDPReceiverSocket.sendto( ack_pkt, address )

      #incrementing pkt number
    pkt_number = pkt_number + 1
 
