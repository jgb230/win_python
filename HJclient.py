
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
print(pip.pep425tags.get_supported())

g_host='172.16.0.17'
g_port=3306
g_user='root'
g_passwd='root'
g_db='sharedata'
g_charset='utf8'

db = pymysql.connect(host=g_host, port=g_port, user=g_user, passwd=g_passwd, db=g_db, charset=g_charset)

#ip = "172.16.2.2:8080"
#ip = "116.62.230.242:9044"
ip = "172.16.2.44:8080"
url1 = "http://"
url2 = "/smartdemo/smatrIvr"
phone=""

def post(postdata):
    url = "http://" + ip + "/smartdemo/smatrIvr"
    headers = {'content-type': 'charset=utf-8'}
    res = requests.post(url, data=postdata, headers = headers)
    print(res.json())
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
    print(re.json())

class MSG():
    phone = ""
    callid = ""
    
    def set(self, phone, callid):
        self.phone = phone
        self.callid = callid


    def enter(self):
        print("post---------enter-------------")
        print(phone)
        indata=('''
                {
                "calleeid":"'''+self.phone+'''",
                "callerid":"8888",
                "callid":"'''+self.callid+'''",
                "errorcode":0,
                "flowdata":"abc",
                "flowid":"abc",
                "notify":"enter"
                }
                ''').encode('utf-8')
        return str(post(indata))

    def message(self, msg, playstate):
        print("post----------asrmessage_notify------------")
        indata=('''
                {
                "asrelapse": 391,
                "asrtextall": "1.识别结果;",
                "asrtype": "aiui",
                "calleeid": "'''+self.phone+'''",
                "callerid": "8888",
                "callid": "'''+self.callid+'''",
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

    def playResult(self, data):
        print("post----------playback_result------------")
        indata=('''
               {
                "calleeid": "'''+self.phone+'''",
                "callerid": "8888",
                "callid": "'''+self.callid+'''",
                "errorcode": 0,
                "flowdata": "'''+data+'''",
                "flowid": "abc",
                "message": "FILE PLAYED",
                "notify": "playback_result"
                }
                ''').encode('utf-8')
        
        return str(post(indata))

    def leave(self):
        print("post----------leave------------")
        indata=('''
                {
                "calleeid":"'''+self.phone+'''",
                "callerid":"8888",
                "callid":"'''+self.callid+'''",
                "errorcode":0,
                "flowdata":"",
                "flowid":"abc",
                "notify":"leave"
                }
                ''').encode('utf-8')
        post(indata)

    def wait(self):
        print("post----------wait------------")
        indata=('''
                {
                "asrstate":false,
                "calleeid":"'''+self.phone+'''",
                "callerid":"8888",
                "callid":"'''+self.callid+'''",
                "duration":8,
                "errorcode":0,
                "flowdata":"",
                "flowid":"9999",
                "message":"_none_",
                "notify":"wait_result"
                }
                ''').encode('utf-8')
        return str(post(indata))

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

def insertType(phone,callid, Type):
    print(phone + "---" + Type)
    cursor = db.cursor()
    gsql = "insert into tesdb001.tb_call_stat values('"+callid+"','"+phone+"',0,'"+Type+"',now()) ON DUPLICATE KEY UPDATE callerid='"+phone+"',type='"+Type+"';"
    print(gsql)
    cont = ""
    try:
        cursor.execute(gsql)
        db.commit()
        cursor.close()
    except:
        print("error")


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
