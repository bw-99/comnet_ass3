from socket import *
from time import time
from struct import *

def writePkt(logFile, procTime, pktNum, event):
    logFile.write('{:1.3f} pkt: {} | {}\n'.format(procTime, pktNum, event))

def writeAck(logFile, procTime, ackNum, event):
    logFile.write('{:1.3f} ACK: {} | {}\n'.format(procTime, ackNum, event))

def writeEnd(logFile, throughput):
    logFile.write('File transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))

def writing_file(data_list,destination):
    dest=destination
    f=open(dest,"wb")
    for i in range(len(data_list)):
        if(i>0 and data_list[i]):
            f.write(data_list[i])
    f.close()

def find_host_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return(ip)

def check_serial(data_list):
    s=0
    for i in range(len(data_list)):
        if(data_list[i] != None):
            s+=1
        else:
            break
    return s


def save_data(data,index_sender,data_list):
    data_list[index_sender]=data

def parsing_header(data):
    header = data[:12]
    upheader = unpack('di', header)
    tm, index_sender = upheader[0], upheader[1]
    return tm,index_sender


if __name__ == '__main__':
    buff = 1400
    SERVER_IP = find_host_ip()
    SERVER_PORT = 10080
    serversocket = socket(AF_INET, SOCK_DGRAM)
    serversocket.bind((SERVER_IP, SERVER_PORT))
    index=0
    length=1
    fp=open("fileAAA_receiving_log.txt","w")
    data, addr = serversocket.recvfrom(buff)
    START = time()
    tm,index_sender=parsing_header(data)
    writePkt(fp,time()-START,index_sender,'received')
    data=data[12:]
    header_2 = data.decode()
    header_2 = header_2.split(',')
    dest = header_2[0][2:][:-1]
    length = eval(header_2[1])
    print(dest,length)
    data_list = [None for x in range(length + 1)]
    data_list[0]=dest
    send_header=pack('di',tm,index_sender)
    serversocket.sendto(send_header, addr)
    writeAck(fp, time() - START, index_sender, 'sent')
    while True:
        data, addr = serversocket.recvfrom(buff)
        tm,index_sender=parsing_header(data)
        writePkt(fp, time() - START, index_sender, 'received')

        index_user = check_serial(data_list)
        if index_sender>length and index_user >= length:
            writing_file(data_list, dest)
            writeEnd(fp,round((length+1)/(time() - START), 3))
            break
        else:
            pass
        data=data[12:]


        if(index_sender <= length ):
            save_data(data,index_sender, data_list)
            send_header = pack('di', tm, index_user)
            serversocket.sendto(send_header, addr)
            writeAck(fp,time()-START,index_user,'sent')



