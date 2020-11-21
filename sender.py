from socket import *
import time

def writing_file(data_list,destination):
    dest=destination
    f=open(dest,"wb")
    p=open("log_sender2.txt","wb")
    for i in range(len(data_list)):
        if i>0:
            f.write(data_list[i])
        p.write(data_list[i])
    f.close()
    p.close()

def read_and_sep(p,buffer,dest):
    data=p.read(buffer)
    sep_data=[]
    sep_data.append(dest.encode())
    k = open("log_sender.txt", "wb")

    while(data):
        k.write(data)
        sep_data.append(data)
        data = p.read(buffer)


    p.close()
    k.close()
    return sep_data

def check_serial(data_list):
    index=0
    for i in range(len(data_list)):
        if(data_list[i].__sizeof__() > 0):
            index+=1
        else:
            return index
    return index

def sending_file(index,window_size,clientsocket,data):
    max=data.index(data[-1])
    rn=window_size if index+window_size<= max else max-index+1
    for j in range(rn):
        k = index+j
        if k >= max:
            k=max
        print(f"Sending {k}th packet...")
        clientsocket.sendto(data[k], ('192.168.0.9', 10080))

def get_ack(clientsocket,ack_list,data_length,data):
    try:
        ack,addr=clientsocket.recvfrom(buffer)
        ack=ack.decode()
        print(ack,'/',data_length)
        index= eval(ack[3:])
        inx=check_serial(ack_list)
        print('inx and index ',inx,index,f'{inx==index}')
        if (inx==index and index>=data_length):
            return 1,index
        elif(index+window_size > data_length):
            ack_list.append(ack)
            return -2,-2
        elif (inx==index):
            ack_list.append(ack)
            return 0, index
        elif (index < inx):
            #ind=inx if inx < index else index
            return -2,-2
    except:
        print("TIME OUT...")
        inx = check_serial(ack_list)
        return -1,inx



buffer=1024

if __name__ == '__main__':
    clientsocket=socket(AF_INET, SOCK_DGRAM)
    clientsocket.settimeout(1)
    IP_ADDRESS=input('IP_ADDRESS : ')
    window_size=eval(input('window_size : '))
    source=input('source : ')
    destination=input('destination : ')
    p = open(source, "rb")
    data=[]
    data=read_and_sep(p,buffer,destination)
    data_length=len(data)-1
    data[0]=f'{data[0]},{data_length}'.encode()
    ack_list=[]
    index=0
    writing_file(data,"abc.jpg")
    sending_file(index, window_size, clientsocket, data)

    while True:
        tag, index= get_ack(clientsocket,ack_list,data_length,data)
        if(tag==-1):    #유실 생김
            print(f"Sending {index}th to {index+window_size}th packet")
            sending_file(index, window_size, clientsocket, data)
        elif (tag == 0):  # tag=0 -> 유실 없이 ack 정상적으로 받음
            if (index + window_size > data_length):
                inx = data_length
            else:
                inx = index + window_size
            print(f"Sending {inx}th packet...")
            clientsocket.sendto(data[inx], ('192.168.0.9', 10080))
        elif (tag==-2):
            pass
        elif(tag==1):   #끝
            clientsocket.sendto(f'END'.encode(),('192.168.0.9', 10080))
            print("End")
            p.close()
            break







"""t = threading.Thread(target=sending_file, args=(index,window_size,clientsocket,data))
            t.daemon = True
            t.start()"""
