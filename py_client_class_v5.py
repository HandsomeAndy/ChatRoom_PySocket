import socket
import sys
import threading
import time
assert sys.version_info >= (3,5)
class CONNECTION(object):
    def __init__(self,rcv_buffer,portno,host):
        self.colormap={}
        self.rcv_buffer = rcv_buffer
        self.portno = portno
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host,portno)
        print('connecting to %s port %s' % server_address)
        self.sock.connect(server_address)
        self.th = threading.Thread(target = self.rcv)
        self.th.start()
    def rcv(self):
        try:
            while True:
                self.data = self.sock.recv(self.rcv_buffer)
                data = self.data.decode()
                if data == "":
                    print('connection closed by server\nclosing receiver')
                    self.close()
                    break
                elif data[-13:] == 'cccconfigcccC':
                    name = data[data.find('~+_=|||')+7:data.find('|||=_+~')]
                    color = data[data.find('CoLoR')+5:data.find('rOloC')]
                    self.colormap.update({name:color})
                    print('\x1b[5;30;44mMembers infomation\x1b[0m: '+color+name+'\x1b[0m')
                elif data == 'rtt':
                    #print('rtt testing')
                    pass
                else:
                    for j in self.colormap.keys():
                        loc = data.find(j)
                        if loc >= 0:
                            data = data[:loc] + self.colormap[j]+ j + '\x1b[0m' + data[loc+len(j):]
                    print('\x1b[6;30;42m'+'received'+'\x1b[0m'+' "%s" ' % data)
        except:
            print('stopping receiver')
            self.close()
    def send(self,msg):
        if msg == 'CLOSE' or (not self.th.isAlive()):
            print('socket closed by user')
            self.close()
        else:
            print('sending...')
            self.sock.sendall(msg.encode('utf-8'))
    def get_rtt(self):
        msg = 'rtt'
        try:
            st = time.time()
            self.sock.sendall(msg.encode('utf-8'))
            while True:
                if self.data.decode() == 'rtt':
                    fi = time.time()
                    self.rtt = (fi - st)
                    msg = '%f' % self.rtt
                    self.sock.sendall(msg.encode('utf-8'))
                    break
        except:
            print('rtt failed')
            self.close()
    def close(self):
        self.sock.close()

connect = 0
try:
    # Send data
    connect = CONNECTION(100,20039,'localhost')
    message = input('Welcome, please input your name: ')
    connect.send(message)
    time.sleep(0.5)
    connect.get_rtt()
    while message != 'CLOSE' and connect.th.isAlive():
        message = input('')
        connect.send(message)
except:
    print('socket interupted')
    if connect:
        connect.close()
        print('socket closed')
    else:
        print('server not found')
        print('program closed')