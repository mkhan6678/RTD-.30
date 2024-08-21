
 # 12 bytes 8 bytes for header 'COMPNETW' and 2 byte checksum and 2 byte length

HEADERSIZE = 12  


def create_checksum(packet_wo_checksum):

    send_msg = packet_wo_checksum
    
    send_msg = ''.join(format(byte, '08b') for byte in send_msg)
    # # Divide sent messages in packets of j bits.
    
    j = 16
    firstbits16 = "" 
    nextbits16 = ""
    twobyte = ""
    firstbit = True
    checksum_sender = '0'
    for bit in send_msg:
                  
         if(j != 0):
            twobyte = twobyte + bit
            j -= 1  
            if(j == 0):
                
                if(firstbit):
                    firstbits16 = twobyte
                    firstbit = False
                else:
                    nextbits16 = twobyte
                    checksum_sender = bin(int(checksum_sender,2) + int(firstbits16, 2) +int(nextbits16, 2))[2:]
                    firstbit = True
                twobyte = ""
                j = 16
    

    # # Calculate the binary total of packets
    Total = bin(int(checksum_sender,2))[2:]


    # Add the overflow bits
    if(len(Total) > j):
        x = len(Total)-j
        Total = bin(int(Total[0:x], 2)+int(Total[x:], 2))[2:]
    if(len(Total) < j):
        Total = '0'*(j-len(Total))+Total
 
    # Calculate complement of Total
    Chk_sum = ''
    for i in Total:
        if(i == '1'):
            Chk_sum += '0'
        else:
            Chk_sum += '1'
    chk_sum_val = int(Chk_sum, 2)

    bytearrsend =  chk_sum_val.to_bytes(2, 'big')    
    return bytearrsend


def verify_checksum(packet):

    packet_inbits = ''.join(format(byte, '08b') for byte in packet)

    # # Divide sent message in packets of j bits.
    
    j = 16
    firstbits16 = "" 
    nextbits16 = ""
    twobyte = ""
    firstbit = True
    recev_sum_chk = '0'
    for bit in packet_inbits:        
         
         if(j != 0):
            twobyte = twobyte + bit
            j -= 1  
            if(j == 0):
                
                if(firstbit):
                    firstbits16 = twobyte
                    firstbit = False
                else:
                    nextbits16 = twobyte
                    recev_sum_chk = bin(int(recev_sum_chk,2) + int(firstbits16, 2) +int(nextbits16, 2))[2:]
                    firstbit = True
                twobyte = ""
                j = 16

    
    chk_sum_bits = packet_inbits[4*j:5*j]
      
    # Calculating the binary sum of packets + checksum
    recev_sum = bin(int(recev_sum_chk,2) + int(chk_sum_bits, 2) )[2:] 
 
    # Adding the overflow bits
    if(len(recev_sum) > j):
        x = len(recev_sum)-j
        recev_sum = bin(int(recev_sum[0:x], 2)+int(recev_sum[x:], 2))[2:]
 
    # Calculating the complement of sum
    recev_chksum = ''
    for i in recev_sum:
        if(i == '1'):
            recev_chksum += '0'
        else:
            recev_chksum += '1'

    totalsum=bin(int(chk_sum_bits,2)+int(recev_chksum,2))[2:]

    # Finding the sum of checksum and received checksum
    total_complement_sum=''

    for i in totalsum:

        if(i == '1'):

            total_complement_sum += '0'
        else:

            total_complement_sum += '1'

    if(int(total_complement_sum,2) == 0):
        return True    
    else:
        return False

def get_seq_num(packet):
  
    length = b''
    packt = packet[10] #read length at position 10th to 11th
    packt2 = packet[11]
    len_data = packt.to_bytes(1,'big') + packt2.to_bytes(1,'big')

    bytes_as_bits = ''.join(format(byte, '08b') for byte in len_data)
    # get the length of string
    length = len(bytes_as_bits)
    # Get last character of string i.e. char at index position len -1
    seq_num = bytes_as_bits[length -1]
    return int(seq_num,2)
      


def make_packet(data_str, ack_num, seq_num):

    # make sure your packet follows the required format!
    tlength = HEADERSIZE + len(data_str) 
    leftshiftedlength = tlength << 2; #left shift operation
     
    ack_no = str(ack_num)
    seq_no = str(seq_num)
    
    #binary represenation of left value
    val = format(leftshiftedlength, '08b')

    # assign acknowledgement no and sequence no to length at 1 & 0 position
    pkts_len_in_binary = bin(int(str(val),2) + int(ack_no,2) + int(seq_no,2))[2:]     

    value = int(pkts_len_in_binary, 2)

    array = bytearray() 

    while value: 
        array.append(value & 0xff)
        value >>= 8
     
    pkt_len_in_byte = bytes(array[::-1])
    int_val = int.from_bytes(pkt_len_in_byte, "big")
    pkt_len_in_bytes = int_val.to_bytes(2, 'big')

    initchecksum = 0

    packt_wo_checksum = bytearray("COMPNETW",'ascii')
    packt_wo_checksum = packt_wo_checksum + (initchecksum.to_bytes(2,'big'))
    packt_wo_checksum = packt_wo_checksum + pkt_len_in_bytes
    packt_wo_checksum = packt_wo_checksum + bytearray(data_str, 'ascii')
    
    #send the initial packet to create checksum function 
    checksum = create_checksum(packt_wo_checksum)

    pktwithchecksum = bytearray("COMPNETW",'ascii')
    pktwithchecksum = pktwithchecksum + checksum
    pktwithchecksum = pktwithchecksum + pkt_len_in_bytes
    pktwithchecksum = pktwithchecksum + bytearray(data_str, 'ascii')

    # return packet 
    return pktwithchecksum



def is_ack(packet):

    #check for ack bit in length field

    length = b''
    #position 10th ack bit
    ack = packet[10] 
    #position 11th seq  bit
    seq = packet[11]
    len_data = ack.to_bytes(1,'big') + seq.to_bytes(1,'big')
    len_bits = ''.join(format(byte, '08b') for byte in len_data)
    # get the length of string
    length = len(len_bits)
    # get char at index position len -2 which is ack no.
    ack_num = len_bits[length -2]
    return int(ack_num,2)