#!/bin/python
#coding=utf-8
import threading
from threading import Thread, Condition
from time import ctime,sleep
import socket
import json
import time
import hashlib
from mySocket import mySocket
from utl import utl
from RWLock import RWLock

class GLClient:
    def __init__(self, ip, port, appid, appkey, tp, version, magic):
        if (appid == "" or appkey == ""):
            print("appid empty or appkey empty")
            return
        self.m_instance = None
        self.m_function_name = None
        self.m_scond = Condition()
        self.m_randomSeed = ""

        self.m_result = 0
        self.m_heartTime = 0
        self.m_appid = appid
        self.m_appkey = appkey
        self.m_type = tp
        self.util = utl(version, magic)

        self.m_rwLock = RWLock()
        self.m_loginId = {}

        self.mysock = mySocket(self, ip, port)

# 注册回调函数
    def registerCallback(self,  instance, function_name):
        self.instance = instance
        self.function_name = function_name
# 调用回调函数
    def callBack(self, param):
        self.instance.__getattribute__(self.function_name)(param)

# 启动收包线程
    def starRecv(self):
        t1 = threading.Thread(target=self.recvMsg)
        t1.setDaemon(True)
        t1.start()

# 收包处理函数 循环处理服务器发送过来的消息
# 消息结构 消息头(14字节)+消息体(json格式) 
# 消息头 长度（4字节）（10 + 消息体长度）+ 校验(4字节 目前没用到) + 消息号(2字节) + 版本号(1字节) + 快捷校验(1字节) + retcode（2字节）

    def recvMsg(self):
        recvlen = 4
        bhead = True
        buff = bytes()
        while (1 == 1):
            self.beatHeart()
            try:
                buff = self.mysock.recv(recvlen)
            except socket.timeout as e:
                print("recv timeout ", e)
                continue
            if (bhead):
                bhead = False
                recvlen = self.util.bytes2int(buff)
               # print("recvlen: %d"%(recvlen))
                buff = bytes()
            else:
                commond = self.util.bytes2short(buff[4:6])
                msg = buff[10:len(buff)].decode()
                sdata = json.loads(msg)
                recvlen = 4
                bhead = True
                buff = bytes()
                print("recv commond %3d %s" %(commond ,msg))
                if (commond == 301): 
                    self.msg301(sdata) 
                elif (commond == 302): 
                    self.msg302(sdata) 
                elif (commond == 102):
                    self.msg102(sdata)
                elif (commond == 104): 
                    self.msg104(sdata) 
                elif (commond == 901): 
                    self.msg901(sdata) 
                elif (commond == 9999):
                    pass
                else: 
                    print("error commond %d"%( commond))

    # 处理301服务器登录返回消息,接收校验码
    def msg301(self, sdata):
        result = 0
        if ("result" in sdata):
            result = sdata["result"]
        
        randomSeed = ""
        if (result != 1):
            print("msg: %s result: %d"% (sdata["msg"], result))
        else:
            if ("randomSeed" in sdata):
                randomSeed = sdata["randomSeed"]
            #print("randomSeed: %s, result %d"% (randomSeed, result))
        self.setSeed(randomSeed, result)
        return 0
    
    #  处理302服务器验证返回消息
    def msg302(self, sdata):
        result = 0
        if ("result" in sdata ):
            result = sdata["result"]
        self.setAuth(result)
        if (result != 1):
            print("msg: %s result: %d"% (sdata["msg"], result))
        #else :
            #print("auth result:%d"% (result))
        
        return 0
    
# 处理102 用户登录返回消息，接收uid
    def msg102(self, sdata):
        result = 0
        if ("result" in sdata):
            result = sdata["result"]
        
        uid = 0
        proId = ""
        if (result != 1):
            print("msg: %s, result: %d"% (sdata["msg"], result))
        else:
            if ("uid" in sdata):
                uid = sdata["uid"]
            if ("seq" in sdata):
                proId = sdata["seq"]
                
            #print("login uid: %d , result: %d"% (uid, result)) 
        
        self.setUid(uid, result, proId)
        return 0
    
# 处理104 用户登出返回消息
    def msg104(self, sdata):
        result = 0
        if ("result" in sdata):
            result = sdata["result"]
        
        uid = 0
        seq = ""
        if (result != 1):
            print("msg: %s, result %d"% (sdata["msg"], result))
        else:
            if ("uid" in sdata):
                uid = sdata["uid"]
            
            if ("seq" in sdata):
                seq = sdata["seq"]
            #print("logout uid: %d, seq: %s"% (uid, seq))
        
        return 0
    
# 处理901 服务器交互消息，调用回调函数
    def msg901(self, sdata):
        result = 0

        if ("result" in sdata):
            result = sdata["result"]
        
        if (result != 1):
            print("msg: %s, result %d"% (sdata["msg"], result))
            return -1
        else :
            self.callBack(sdata)
            #print("aichat result: %d"% (result))
        
        return 0
    
# 设置uid
    def setUid(self, uid, result, proId):
        self.m_rwLock.lock_write()
        self.m_result = result
        self.m_loginId[uid] = proId
        self.m_rwLock.release_write()

# 设置校验码
    def setSeed(self, seed, result):
        self.m_scond.acquire()
        self.m_randomSeed = seed
        self.m_result = result
        self.m_scond.notify_all()
        self.m_scond.release()

# 设置验证返回码
    def setAuth(self, result):
        self.m_scond.acquire()
        self.m_result = result
        self.m_scond.notify_all()
        self.m_scond.release()

# 给服务器发送消息
    def sendMsg(self, commond, data):
    
        sdata = json.dumps(data)
        l = 10 + len(sdata.encode('utf-8'))
        bs = bytes(self.util.head(l, commond))
        #print("head :",bs.hex())
        print("send commond %3d %s"% (commond, sdata))
        try:
            ret = self.mysock.send(bs + sdata.encode('utf-8'))
        except Exception  as e:
            print(e)
            ret = -1
        return ret

# 发送心跳包
    def beatHeart(self):
        nowTime = int(time.time())
       # print("nowtime %d heart %d"%(nowTime, self.m_heartTime))
        if (nowTime - self.m_heartTime >= 30):
            self.m_heartTime = nowTime
            data = {}
            #print(self.m_heartTime)
            data["nowTime"] = self.m_heartTime
            self.sendMsg(9999, data)

# 发送服务器登录消息
    def servLogin(self):
        data = {}
        #print(int(time.time()))
        data["servType"] = self.m_type
        data["appid"] = self.m_appid

        ret = self.sendMsg(201, data)

        if (ret < 0):
            print("send mes  errno : %d"%(ret))
            return ret
        elif( ret == 0):
            print("send socket close ")
            return -1
            

        self.m_scond.acquire()
        self.m_scond.wait()
        ret = self.m_result
        self.m_scond.release()

        return 0 if ret==1 else -1

# 发送服务器验证消息    
    def servAuth(self):
        data = self.m_randomSeed + self.m_appkey
        m1 = hashlib.md5()
        m1.update(data.encode("utf-8"))
        sign = m1.hexdigest()

        data = {}
        #print(int(time.time()))
        data["sign"] = sign
        data["appid"] = self.m_appid

        ret = self.sendMsg(202, data)
        if (ret < 0):
            print("send mes  errno : %d"%(ret))
            return ret
        elif( ret == 0):
            print("send socket close ")
            return -1
        

        self.m_scond.acquire()
        self.m_scond.wait()
        ret = self.m_result
        self.m_scond.release()

        return 0 if ret==1 else -1

# 发送交互消息
    def aichat(self, msg, uid):
        data = {}
        #print(int(time.time()))
        data["uid"] = uid
        data["content"] = msg
        data["appid"] = self.m_appid

        ret = self.sendMsg(801, data)
        if (ret < 0):
            print("send mes  errno : %d"%(ret))
            return ret
        elif( ret == 0):
            print("send socket close ")
            return -1
        
        
        return 0
       
# 发送用户登录消息
    def login(self, proId, uid):
        data = {}
        #print(int(time.time()))
        data["uname"] = proId
        data["passwd"] = ""
        data["keytp"] = "openid"
        data["appid"] = self.m_appid
        data["seq"] = proId

        ret = self.sendMsg(2, data)
        if (ret < 0):
            print("send mes  errno : %d"%(ret))
            return ret
        elif( ret == 0):
            print("send socket close ")
            return -1
        tmpid = 0
        while (True):
            self.m_rwLock.lock_read()
            tmpid = self.recvedUid(proId)
            ret = self.m_result
            self.m_rwLock.release_read()
            if ( tmpid != 0 ):
                break
        uid.append(tmpid)
        return 0 if ret==1 else -1

    def recvedUid(self, proId):
        for key in self.m_loginId:
            if self.m_loginId.get(key) == proId :
                return int(key)
            
        return 0
# 发送用户登出消息
    def logout(self, proId, uid):

        data = {}
        #print(int(time.time()))
        data["uid"] = uid
        data["appid"] = self.m_appid
        data["seq"] = proId
        
        ret = self.sendMsg(4, data)
        if (ret < 0):
            print("send mes  errno : %d"%(ret))
            return ret
        elif( ret == 0):
            print("send socket close ")
            return -1
        self.m_rwLock.lock_read()
        self.m_loginId.pop(uid)
        self.m_rwLock.release_read()
        return 0
# 初始化
    def initGL(self):
        self.mysock.connect()
        print("connect success")
        self.starRecv()
        ret = self.servLogin()
        if (ret != 0):
            print("servLogin error")
            return -1
        ret = self.servAuth()
        if (ret != 0):
            print("servAuth error")
            return -1
        return 0
    
