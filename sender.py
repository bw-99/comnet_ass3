from socket import *
import time
import threading
from struct import *




def writePkt(logFile, procTime, pktNum, event):
    logFile.write('{:1.3f} pkt: {} | {}\n'.format(procTime, pktNum, event))

def writeAck(logFile, procTime, ackNum, event):
    logFile.write('{:1.3f} ACK: {} | {}\n'.format(procTime, ackNum, event))

def writeEnd(logFile, throughput, avgRTT):
    logFile.write('File transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))
    logFile.write('Average RTT : {:.1f} ms\n'.format(avgRTT))


def writing_file(data_list,destination):
    dest=destination
    f=open(dest,"wb")
    for i in range(len(data_list)):
        if i>0:
            f.write(data_list[i])
    f.close()


def read_and_sep(p,buffer,dest):
    data=p.read(buffer)
    sep_data=[]
    sep_data.append(dest.encode())
    while(data):
        sep_data.append(data)
        data = p.read(buffer)
    p.close()
    return sep_data

def check_serial(data_list):
    for i in range(len(data_list)):
        if(not data_list[i][0]):
            break
    return i

def parsing_header(data):
    header = data[:12]
    upheader = unpack('di', header)
    time, index = upheader[0], upheader[1]
    return time,index

def sending_files(index,window_size,clientsocket,data,fp):
    max=data.index(data[-1])
    rn=window_size if index+window_size<= max else max-index+1
    for j in range(rn):
        k = index+j
        if k >= max:
            k=max
        writePkt(fp,time.time()-START,k,'sent')
        header = pack('di', time.time()-START ,k)
        clientsocket.sendto(header+data[k], ('192.168.0.9', 10080))

def send_Afile(index,window_size,clientsocket,data,fp):
    inx=index+window_size
    cur=time.time()-START
    writePkt(fp,cur,inx,'sent')
    header=pack('di',cur,inx)
    clientsocket.sendto(header+data[index+window_size], ('192.168.0.9', 10080))

def cal_average_RTT(ack_list,index):
    t=0
    divider=index+1
    for i in range(index):
        t+=ack_list[i][2]-ack_list[i][1]
    RTT=t/divider if t/divider > 0.01 else 0.01
    ack_list[index][3] = RTT


def get_ack(clientsocket,ack_list,data_length,data,fp):
    while True:
        try:
            ack, addr = clientsocket.recvfrom(buff)
            tm,index = parsing_header(ack)
            inx=check_serial(ack_list)
            ack_list[index][0] += 1
            ack_list[index][1] = tm
            ack_list[index][2] = time.time()-START

            writeAck(fp,tm,index,'received')

            cal_average_RTT(ack_list,index)

            average_RTT=ack_list[index][3]
            TOTAL_AVERAGE_RTT=average_RTT
            clientsocket.settimeout(average_RTT)

            if ack_list[index][0] >= 3: #3duple
                writePkt(fp, tm, index, '3 duplicated ACKs')
                writePkt(fp, tm, index+1, 'retransmitted')
                t = threading.Thread(target=sending_files, args=(index,1,clientsocket,data,fp))
                t.daemon = True
                t.start()
            elif (index>=data_length):  #finish
                cur = round(time.time() - START, 3)
                header = pack('di', cur, data_length+1)
                clientsocket.sendto(header, ('192.168.0.9', 10080))

                writePkt(fp, cur, data_length + 1, 'sent')
                final = time.time() - START
                writeEnd(fp,(data_length+1)/final,ack_list[-1][3]*100)

                break
            elif (inx==index and index+window_size <= data_length): #get proper ack
                t = threading.Thread(target=send_Afile, args=(inx,window_size,clientsocket,data,fp))
                t.daemon = True
                t.start()
            else:   #get unproper ack
                pass

        except:
            inx = check_serial(ack_list)
            cur=time.time()-START
            timeoutvalue = round(TOTAL_AVERAGE_RTT,3)
            writePkt(fp, cur, inx, f'timeout since {round(ack_list[inx][2]-ack_list[inx][1],3)} (timeout value {timeoutvalue})')
            t = threading.Thread(target=sending_files, args=(inx, window_size,clientsocket, data,fp))
            t.daemon = True
            t.start()





buff=1350

if __name__ == '__main__':
    TOTAL_AVERAGE_RTT=0
    clientsocket=socket(AF_INET, SOCK_DGRAM)
    clientsocket.settimeout(1)
    IP_ADDRESS=input('IP_ADDRESS : ')
    window_size=eval(input('window_size : '))
    srcFilename=input('source : ')
    dstFilenmae=input('destination : ')
    p = open(srcFilename, "rb")
    data=[]
    data=read_and_sep(p,buff,dstFilenmae)
    p.close()
    data_length=len(data)-1
    print(data_length)
    data[0]=f'{data[0]},{data_length}'.encode()
    ack_list=[[0,0,0,0] for x in range(data_length+1)]
    index=0
    START=time.time()
    fp = open("fileAAA_sending_log.txt", 'w')

    sending_files(index, window_size, clientsocket,data,fp)
    get_ack(clientsocket,ack_list,data_length,data,fp)

    fp.close()









"""t = threading.Thread(target=sending_file, args=(index,window_size,clientsocket,data))
            t.daemon = True
            t.start()"""
