#!/bin/python
#coding=utf-8
import threading 
from clientAPI import GLClient
from time import sleep
################################ demo
class callback():
    def callfunc(self, param):
        print("callback : %s"%(param))

def login(client, i):
    proid = "jgbtest" + str(i)
    msg = "清除肾炎标签1"
    uid = []
    ret = client.login(proid, uid)
    if (ret != 0):
        print("login error ")
        return
    print("login  proid %s uid %d"% (proid, uid[0]))

    ret = client.aichat(msg, uid[0])
    sleep(1)
    print("logout ")
    ret = client.logout(proid, uid[0])
    if (ret != 0):
        print("logout error ")
        return

def main():
    cb = callback()
    appId = "4.00002"
    appKey = "!4j7oTLOXIKOFW@P"
    
    ip = "172.16.0.27"
    port = 2345
    version = 1
    magic = b'$'

    print("init ")
    client = GLClient(ip, port, appId, appKey, 1, version, magic)
    client.registerCallback(cb, cb.callfunc.__name__)
    ret = client.initGL()
    if (ret != 0):
        print("init error ")
        return
    
    t1 = threading.Thread(target=login, args=(client, 1))
    t1.setDaemon(True)
    t2 = threading.Thread(target=login, args=(client, 2))
    t2.setDaemon(True)
    t3 = threading.Thread(target=login, args=(client, 3))
    t3.setDaemon(True)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

if __name__ == '__main__':
    main()

