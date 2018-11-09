
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
import pip
import zmq,json

print(pip.pep425tags.get_supported())

g_host='172.16.0.17'
g_port=3306
g_user='root'
g_passwd='root'
g_db='tesdb001'
g_charset='utf8'

db = pymysql.connect(host=g_host, port=g_port, user=g_user, passwd=g_passwd, db=g_db, charset=g_charset)

broker = "tcp://172.16.0.17:3130"

class TESMSG():
    def build602(self, phone):
        dic = {}
        dic["cmd"] = 602
        dic["uid"] = phone
        dic["playerID"] = 0
        dic["robotType"] = 1
        msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
        return msg

    def build600(self, robotId, phone, service):
        dic = {}
        dic["cmd"] = 600
        dic["uid"] = phone
        dic["robotid"] = robotId
        dic["user_service"] = service
        msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
        return msg

    def buildPlayback():
        Map<String, Object> map = new HashMap<String, Object>()
        map.put("cmd", 1403)
        map.put("robotid", callTemp.robotId)
        //map.put("uid", calleeid)
        map.put("uid", callTemp.userId)
        map.put("result", 0)
        map.put("play_time", 0)
        return JSON.toJSONString(map)


    def buildTimeoutShortMsg(callTemp):

        Map<String, Object> map = new HashMap<String, Object>()
        map.put("cmd", 1401)
        map.put("robotid", callTemp.robotId)
        //map.put("uid", calleeid)
        map.put("uid", callTemp.userId)
        return JSON.toJSONString(map)


    def buildTimeoutLongMsg(callTemp):
        Map<String, Object> map = new HashMap<String, Object>()
        map.put("cmd", 1402)
        map.put("robotid", callTemp.robotId )
        //map.put("uid", calleeid)
        map.put("uid", callTemp.userId )
        return JSON.toJSONString(map)


    def buildLeaveMsg(callTemp):
        Map<String, Object> map = new HashMap<String, Object>()
        map.put("cmd", 601)
        map.put("robotid", callTemp.robotId )
        //map.put("uid", calleeid)
        map.put("uid", callTemp.userId )
        return JSON.toJSONString(map)

    def buildMsgMsg(message, callTemp):
        Map<String, Object> map = new HashMap<String, Object>()
        map.put("cmd", 801)
        map.put("channel", "dialog")
        map.put("content", message)
        map.put("robotid", callTemp.robotId )
        map.put("scene", "")
        //map.put("uid", calleeid)
        map.put("uid", callTemp.userId )
        return JSON.toJSONString(map)
                    

    def searchVbContent(self, taskid):
        record = self.db.selectVerbalContent(taskid)
        if record == None:
            logger.warning("no vb_content taskId:%s!",taskid)
        content = record.get('vb_content')
        return content

    def reportDailFailed(self, newest):
        context = zmq.Context()  
        socket = context.socket(zmq.DEALER)  
        socket.connect(broker) 
        phone = newest.get('cr_mobile')
        taskid = newest.get('cr_taskid')

        msg602 = self.build602(phone)
        logger.info("msg602 %s!",msg602.decode("utf-8"))
        socket.send(msg602)
        cmd = 0
        robotId = ""
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN) 
        socks = dict(poller.poll(1000))

        if socks.get(socket) == zmq.POLLIN:  
            message = socket.recv_multipart()  
            tmp = ""
            for row in message:
                tmp = tmp + row.decode("utf-8")
            data = json.loads(tmp)
            if 'cmd' in data:
                cmd = json.loads(tmp)['cmd']
                if cmd != 700:
                    logger.warning("602 recv cmd is not 700!")
                    return
            else:
                logger.warning("602 recv no cmd!")
                return
            if 'robotList' in data and 'robotID' in json.loads(tmp)['robotList'][0]:
                robotId = json.loads(tmp)['robotList'][0]['robotID']
            else:
                logger.warning("602 recv no robotList!")
                return

        if robotId == "":
            print("602 recv no cmd!")
            return
        msg = self.searchVbContent(taskid)
        msg = msg + "未接通"
        msg600 = self.build600(robotId, phone, msg)
        logger.info("msg600 %s!",msg600.decode("utf-8"))
        socket.send(msg600)

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
    cursor = db.cursor()
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


def getAIContent(id):
    cursor = db.cursor()
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


def CStes():
    phone="17794589041"
    enter(phone)
    time.sleep(3)
    message(phone, "1.是的。", "false")
    time.sleep(4)
    message(phone, "1.没钱。", "false")
    leave(phone)

class myWind(QWidget):
    msg = MSG()
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))

        #textedit
        self.textbox = QTextEdit(self)
        self.textbox.move(20, 30)
        self.textbox.resize(300, 400)
        
        #label
        self.lbl1 = QLabel(self)
        self.lbl1.setText(url1)
        self.lbl1.move(20, 13)

        #label
        self.lbl2 = QLabel(self)
        self.lbl2.setText(url2)
        self.lbl2.move(200, 13)

        #label
        self.lblPhone = QLabel(self)
        self.lblPhone.setText("电话号码")
        self.lblPhone.move(23, 463)

        #lineedit
        self.linebox = QLineEdit(self)
        self.linebox.setText(ip)
        self.linebox.move(60, 10)

        #lineedit
        self.linePhone = QLineEdit(self)
        self.linePhone.move(100,460)
        self.linePhone.setText(phone)
        self.linePhone.resize(120, 20)

        #lineedit
        self.lineMsg = QLineEdit(self)
        self.lineMsg.move(20, 490)
        self.lineMsg.resize(200, 20)
        self.lineMsg.returnPressed.connect(self.msgMsg)

        #combox
        self.cbox = QComboBox(self)
        self.cbox.insertItem(0,self.tr("DK"))
        self.cbox.insertItem(1,self.tr("CS"))
        self.cbox.insertItem(2,self.tr("GP"))
        self.cbox.move(130,522)
        
        #button
        self.btn = QPushButton('退出', self)
        self.btn.clicked.connect(lambda:self.msgLeave())
        self.btn.setToolTip('This is a <b>QPushButton</b> widget')
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(230,520)
        self.btn.setEnabled(False)

        self.btnReset = QPushButton('重置', self)
        self.btnReset.clicked.connect(lambda:self.reset())
        self.btnReset.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnReset.resize(self.btnReset.sizeHint())
        self.btnReset.move(20,520)

        self.btnEnter = QPushButton('发送登录', self)
        self.btnEnter.clicked.connect(lambda:self.msgEnter())
        self.btnEnter.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnEnter.resize(self.btnEnter.sizeHint())
        self.btnEnter.move(230,460)

        self.btnMsg = QPushButton('发送消息', self)
        self.btnMsg.clicked.connect(lambda:self.msgMsg())
        self.btnMsg.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnMsg.resize(self.btnMsg.sizeHint())
        self.btnMsg.move(230,490)
        self.btnMsg.setEnabled(False)

        self.btnleav1 = QPushButton('用户暂离', self)
        self.btnleav1.clicked.connect(lambda:self.msgWait())
        self.btnleav1.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnleav1.resize(self.btnleav1.sizeHint())
        self.btnleav1.move(20,435)
        self.btnleav1.setEnabled(False)

        
        #Widget
        self.setGeometry(500,700,700,520)
        self.setWindowTitle('CStes')
        self.setWindowIcon(QIcon('ai.png'))
        self.resize(350, 550)
        #self.move(300, 300) 位置
        self.center()
        self.show()
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "确定退出？",
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def msgEnter(self):
        global phone
        global ip
        ip = self.linebox.text()
        phone=self.linePhone.text()
        Type=self.cbox.currentText()
        if len(phone) == 0 :
            reply = QMessageBox.question(self, '提示', "没有电话号码",
                                     QMessageBox.Yes, QMessageBox.Yes)
            return
        self.textbox.moveCursor(QTextCursor.End)
        callid = "2c4146f8-6afe-11e8-8cb2-" + phone
        self.msg.set(phone, callid)
        print(phone)
        insertType(self.msg.phone, self.msg.callid, Type)
        content = self.msg.enter()
        txt = "机器人:" + tansContent(content)
        self.textbox.append(txt)

        self.btn.setEnabled(True)
        self.btnMsg.setEnabled(True)
        self.btnleav1.setEnabled(True)

    def msgLeave(self):
        self.msg.leave()

    def msgWait(self):
        content = self.msg.wait()
        print("content:" + content)
        txt = "机器人:" + tansContent(content)
        self.textbox.append(txt)
        
    def msgMsg(self):
        self.textbox.moveCursor(QTextCursor.End)
        if len(self.lineMsg.text()) == 0 :
            reply = QMessageBox.question(self, '提示', "内容为空",
                                     QMessageBox.Yes, QMessageBox.Yes)
            return
        content = "用户  :" + self.lineMsg.text()
        self.textbox.append(content)
        content = self.msg.message(self.lineMsg.text(), "false")
        self.lineMsg.setText("")
        print("content:" + content)
        txt = "机器人:" + tansContent(content)
        self.textbox.append(txt)

        content = self.msg.playResult("")
        while content != "" :
            print("content:" + content)
            txt = "机器人:" + tansContent(content)
            self.textbox.append(txt)
            content = self.msg.playResult("")
        
    def reset(self):
        self.textbox.setText("")
        self.linePhone.setText("")
        
def win():
    app = QApplication(sys.argv)

    w = myWind()
   
    sys.exit(app.exec_())    

def main():
    #CStes()
    win()

if __name__ == '__main__':
    main()
