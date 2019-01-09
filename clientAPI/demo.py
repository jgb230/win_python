#!/bin/python
#coding=utf-8
import threading 
from clientAPI import GLClient
from time import sleep
################################ demo
class callback():
    def callfunc(self, param):
        print("callback : %s"%(param))

def login(client, appid, i):
    proid = "jgbtest" + str(i)
    msg = "清除肾炎标签1"
    uid = []
    ret = client.login(appid, proid, uid)
    if (ret != 0):
        print("login error ")
        return
    print("login  proid %s uid %d"% (proid, uid[0]))

    ret = client.aichat(appid, msg, uid[0])
    sleep(1)
    print("logout ")
    ret = client.logout(appid, proid, uid[0])
    if (ret != 0):
        print("logout error ")
        return

def main():
    cb = callback()
    appid = "4.00002"
    
    info = {}
    info["app"] = []
    info["ip"] = "172.16.0.27"
    info["port"] = 2345
    info["version"] = 1
    info["magic"] = b'$'
    info["instance"] = cb
    info["function_name"] = cb.callfunc.__name__

    app = {}
    app["appid"] = "4.00002"
    app["appkey"] = "!4j7oTLOXIKOFW@P"
    app["type"] =1
    info["app"].append(app)

    print("init ")
    client = GLClient(info)
    ret = client.initGL()
    if (ret != 0):
        print("init error ")
        return
    
    t1 = threading.Thread(target=login, args=(client, appid, 1))
    t1.setDaemon(True)
    t2 = threading.Thread(target=login, args=(client, appid, 2))
    t2.setDaemon(True)
    t3 = threading.Thread(target=login, args=(client, appid, 3))
    t3.setDaemon(True)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

if __name__ == '__main__':
    main()

