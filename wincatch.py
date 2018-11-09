
#!/usr/bin/env python3
# coding=utf-8

import zmq
import json
import pymysql

g_host='172.16.0.17'
g_port=3306
g_user='root'
g_passwd='root'
g_db='sharedata'
g_charset='utf8'

db = pymysql.connect(host=g_host, port=g_port, user=g_user, passwd=g_passwd, db=g_db, charset=g_charset)

class dbAccess:
  
    def selectVerbalContent(self, taskid):
        sql = "select vb_content from sharedata.tb_verbal where vb_uuid =(select task_verbal from sharedata.tb_task where task_id='%s')"%(taskid)
        print(sql)
        records = None
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except:
            print("Error: unable to selectAllTasksById by %s."%(taskid))
        return records[0]


def build602(phone):
        msg=('''
                {
                "cmd":602,
                "uid":"'''+phone+'''",
                "playerID":0,
                "robotType":1
                }
                ''').encode('utf-8')
        return msg

def build600(robotId, phone, msg):
        msg=('''
                {
                "cmd":600,
                "robotid":"'''+robotId+'''",
                "uid":"'''+phone+'''",
                "user_service":"'''+msg+'''"
                }
                ''').encode('utf-8')
        return msg

def build602_dict(phone):
    dic = {}
    dic["cmd"] = 602
    dic["uid"] = phone
    dic["playerID"] = 0
    dic["robotType"] = 1
    msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
    return msg

def build600_dict(robotId, phone, service):
    dic = {}
    dic["cmd"] = 600
    dic["uid"] = phone
    dic["robotid"] = robotId
    dic["user_service"] = service
    print(dic)
    msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
    return msg

def searchVbContent(taskid):
        db = dbAccess()
        record = db.selectVerbalContent(taskid)
        print(record)
        content = record[0]
        return content

def sendFailedMsg():
        context = zmq.Context()  
        socket = context.socket(zmq.DEALER)  
        socket.connect("tcp://172.16.0.17:3130") 
        phone = "18600227230"
        taskid = "TK2018060002"
        cmd = 0
        robotId = ""
        msg602 = build602_dict(phone)
        socket.send(msg602)
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN) 
        socks = dict(poller.poll(1))
        if socks.get(socket) == zmq.POLLIN:
            message = socket.recv_multipart()
            tmp = ""
            for row in message:
                tmp = tmp + row.decode("utf-8")
            data = json.loads(tmp)
            if 'cmd' in data:
                cmd = json.loads(tmp)['cmd']
            if 'robotList' in data and 'robotID' in json.loads(tmp)['robotList'][0]:
                robotId = json.loads(tmp)['robotList'][0]['robotID']
        print(cmd)
        print(robotId)
        msg = searchVbContent(taskid)
        msg = (msg + "未接通")
        print(msg)
        msg600 = build600_dict(robotId, phone, msg)
        print(msg600)
        socket.send(msg600)
        
if __name__ == "__main__":
    sendFailedMsg()
