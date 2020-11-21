from socket import *
import threading
from time import time


def writing_file(data_list,destination,length):
    dest=destination
    f=open(dest,"wb")
    p=open("log_rec.txt","wb")
    for i in range(len(data_list)-1):
        f.write(data_list[i])
        p.write(data_list[i])
    f.close()
    p.close()

def find_host_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return(ip)

def check_serial(data_list):
    index=0
    for i in range(len(data_list)):
        if(data_list[i].__sizeof__() > 0):
            index+=1
        else:
            return index
    return index

def createServer(data,index,data_list):     #주는대로 받는 문제
    
    print(f"Recieving {index}th packet...")
    print(index)
    print(f"Saving {index}th packet...\n\n")
    data_list.append(data)




if __name__ == '__main__':
    buffer = 1024
    SERVER_IP = find_host_ip()
    SERVER_PORT = 10080
    serversocket = socket(AF_INET, SOCK_DGRAM)
    serversocket.bind((SERVER_IP, SERVER_PORT))

    data_list=[]
    window_size=40
    f=None
    index=0
    length=1
    while True:
        while True:
            data, addr = serversocket.recvfrom(buffer)
            index = check_serial(data_list)
            try:
                header = data.decode()
                header = header.split(',')
                dest, length = header[0], eval(header[1])
                dest = dest[2:][:-1]
                print(dest, length)
                serversocket.sendto(f'ACK{index}'.encode(), addr)
                index+=1
            except:
                if(index <= length ):
                    createServer(data, index, data_list)
                    serversocket.sendto(f'ACK{index}'.encode(), addr)
                    print(f"sending ACK{index}...\n\n")
                    index+=1
                else:
                    writing_file(data_list, dest, length)
                    print("End")
                    index = 0
                    length = 1
                    break

