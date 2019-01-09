#!/bin/python
#coding=utf-8
import socket

class mySocket:
    def __init__(self, client, ip, port):
        
        self.sock = None
        self.m_ip = ip
        self.m_port = port
        self.client = client
    def connect(self):
        try:
            self.sock = socket.socket()
            self.sock.settimeout(20)
            self.sock.connect((self.m_ip, self.m_port))
        except Exception as e:
            print("socket error %s"%(e))

    def close(self):
        self.sock.close()

    def recv(self, length):
        #print("to recv %d"%(length))
        left = length
        right = 0
        buff = bytes()
        recvbuff = bytes()
        while (left > 0):
            try:
                recvbuff = self.sock.recv(length)
            except socket.timeout as e:
                raise e
            except socket.error as e:
                print("recv socket error", e)
                if (self.reconnect() != 0):
                    return bytes()
            buff = buff + recvbuff
            bl = len(buff)
            left = left - bl
            right = right + bl
            #print("left: %d right %d len: %d"%(left, right, len(recvbuff)))

        return buff


    def reconnect(self):
        retime = 0
        while (retime < 3):
            try:
                self.sock = socket.socket()
                self.sock.connect((self.m_ip, self.m_port))
                for i in self.client.m_apps:
                    appid = i["appid"]
                    appkey = i["appkey"]
                    tp = i["type"]
                    ret = self.client.servLogin(appid, tp)
                    if (ret != 0):
                        print("servLogin error")
                        return -1
                    ret = self.client.servAuth(appid, appkey)
                    if (ret != 0):
                        print("servAuth error")
                        return -1
                break
            except Exception as e:
                print("reconnect socket error %s"%(e))
        if (retime == 3):
            return -1
        return 0

    def send(self, data):
        right = 0
        leng = len(data)
        while (right < leng):
            try:
                sendlen = self.sock.send(data[right:leng])
            except socket.error as e:
                print("socket send error ", e)
                if (self.reconnect() != 0):
                    return 0
            except Exception as e:
                print(" socket send error ", e)
                continue
            right = right + sendlen
        return leng
