
#!/usr/bin/env python3
# coding=utf-8


import requests
import time

from PyQt5.QtGui import *  
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import QLineEdit
import sys
import pymysql
import threading
from pymysqlpool import ConnectionPool

config = {
    'pool_name': 'test',
    'host': '172.16.0.17',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'tesdb001',
    'pool_resize_boundary': 100,
    'enable_auto_resize': True,
    "charset": 'utf8'
    # 'max_pool_size': 10
}


def conn_pool():
    # pool = MySQLConnectionPool(**config)
    pool = ConnectionPool(**config)
    # pool.connect()
    # print(pool)
    return pool

g_host='172.16.0.17'
g_port=3306
g_user='root'
g_passwd='TELEPHONE'
g_db='tesdb001'
g_charset='utf8'

db = pymysql.connect(host=g_host, port=g_port, user=g_user, passwd=g_passwd, db=g_db, charset=g_charset)

#ip = "172.16.2.2:8080"
#ip = "116.62.230.242:9044"
ip = "121.196.204.197:18080"
url1 = "http://"
url2 = "/smartdemo/smatrIvr"


def post(postdata):
    #print("postdata:"+postdata.decode("utf-8"))
    url = "http://" + ip + "/smartdemo/smatrIvr"
    headers = {'content-type': 'charset=utf-8'}
    res = requests.post(url, data=postdata, headers = headers)
    #print(res.json())
    ret = ""
    if "params" not in res.json():
        ret = ""
    elif "prompt" not in res.json()['params']:
        ret = ""
    else:
        ret = res.json()['params']['prompt']
    return ret

def get():
    url = "http://" + ip + "/smartdemo/smatrIvr?notify=enter&&charset=UTF-8"
    re = requests.get(url)
    #print(re.json())

def enter(phone,callid):
    #print("post---------enter-------------")
    #print(phone)
    indata=('''
            {
            "calleeid":"'''+phone+'''",
            "callerid":"8888",
            "callid":"'''+callid+'''",
            "errorcode":0,
            "flowdata":"abc",
            "flowid":"abc",
            "notify":"enter"
            }
            ''').encode('utf-8')
    return str(post(indata))

def message(phone, msg, playstate,callid):
    #print("post----------asrmessage_notify------------")
    indata=('''
            {
            "asrelapse": 391,
            "asrtextall": "1.识别结果;",
            "asrtype": "aiui",
            "calleeid": "'''+phone+'''",
            "callerid": "8888",
            "callid": "'''+callid+'''",
            "errorcode": 0,
            "flowdata": "流程选择",
            "flowid": "abc",
            "message": "'''+msg+'''",
            "notify": "asrmessage_notify",
            "speakms": 1162,
            "playms": 20,
            "playstate": '''+playstate+'''
            }
            ''').encode('utf-8')
    
    return str(post(indata))

def playResult(phone, data,callid):
    #print("post----------playback_result------------")
    indata=('''
           {
            "calleeid": "'''+phone+'''",
            "callerid": "8888",
            "callid": "'''+callid+'''",
            "errorcode": 0,
            "flowdata": "'''+data+'''",
            "flowid": "abc",
            "message": "FILE PLAYED",
            "notify": "playback_result"
            }
            ''').encode('utf-8')
    
    post(indata)

def leave(phone,callid):
    #print("post----------leave------------")
    indata=('''
            {
            "calleeid":"'''+phone+'''",
            "callerid":"8888",
            "callid":"'''+callid+'''",
            "errorcode":0,
            "flowdata":"",
            "flowid":"abc",
            "notify":"leave"
            }
            ''').encode('utf-8')
    post(indata)

def tansContent(content):
    if len(content) == 0:
        return ""
    
    lctt=content.split(",")
    ret = ""
    for i in lctt:
        ltemp=i.split("/")
        file=ltemp[-2]+"/"+ltemp[-1][0:ltemp[-1].find("'")]
        print(ltemp[-1])
        print(file)
        if len(file) > 60:
            ret = ret+getContent(file)
        else:
            ret = ret+getAIContent(file)
    #print(ret)
    return ret
        
def getContent(id):
    with conn_pool().connection() as conn:
        cursor = conn.cursor()
        gsql = "SELECT content FROM tesdb001.tb_tencent_content WHERE id='"+id+"';"
        cont = ""
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw[0]
            cursor.close()
        except:
            print("error")
        return cont

def insertType(phone, Type):
    #print(phone + "---" + Type)
    with conn_pool().connection() as conn:
        cursor = conn.cursor()
        gsql = "update `tesdb001`.`tb_call_stat` set callerid = '"+phone+"' , type = '"+Type+"' where callid ='1fe74812-e376-4319-b335-3de1b494325c';"
        #print(gsql)
        cont = ""
        try:
            cursor.execute(gsql)
            conn.commit()
            cursor.close()
        except Exception as err:
            print("error" , err)


def insertRecord(phone, status):
    #print(phone + "---" + str(status))
    with conn_pool().connection() as conn:
        cursor = conn.cursor()
        gsql = ("insert into tesdb001.tb_callrecord(cr_taskid,"+
                "cr_userid, cr_mobile, cr_status, cr_calltime)"+
                "values ('TK201805300001','user0001','%s',%d,now(3));"
                % (phone, status))
        #print(gsql)
        cont = ""
        try:
            cursor.execute(gsql)
            conn.commit()
            cursor.close()
        except Exception as err:
            print("error：" , err)

def getAIContent(id):
    with conn_pool().connection() as conn:
        cursor = conn.cursor()
        gsql = "SELECT content FROM tesdb001.tb_ai_content WHERE id='"+id+"';"
        cont = ""
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw[0]
            cursor.close()
        except:
            print("error")
        return cont


def CStes(tail,phone,callid):
    
    insertRecord(phone, 3)
    enter(phone,callid)
    time.sleep(1)
    message(phone, "1.没有。", "false",callid)
    time.sleep(1)
    message(phone, "1.不用。", "false",callid)
    leave(phone,callid)
  

def main():
    #CStes()
    i=0
    list=[]
    for i in range(0,500):
        tail = ("%04d" % i)
        phone="1860004"+tail
        callid="1fe74812-e376-4319-b335-3de1b494"+tail
    
        list.append(threading.Thread(target=CStes, args=(tail,phone,callid,)))
    for i in list:
        i.start()
    for i in list:
        i.join()

if __name__ == '__main__':
    main()
