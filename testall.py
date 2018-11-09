
#!/usr/bin/env python3
# coding=utf-8
from logging.handlers import TimedRotatingFileHandler
import logging

import requests
import time

from PyQt5.QtGui import *  
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import QLineEdit
from PyQt5 import sip
import sys
import pymysql
import pip
from pymysqlpool import ConnectionPool

loglevel = logging.DEBUG
logfile = "./tescs.log"

# logHandler = RotatingFileHandler(logfile, mode='a', maxBytes=50*1024*1024, backupCount=10, encoding=None, delay=0)
logHandler = TimedRotatingFileHandler(logfile, when='D', interval=1, backupCount=20)
#logFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
logFormatter = logging.Formatter('%(asctime)s %(filename)-12s[line:%(lineno)d] %(thread)d %(levelname)s %(message)s')

logHandler.setFormatter(logFormatter)
logger = logging.getLogger('')
logger.addHandler(logHandler)
logger.setLevel(loglevel)

dbConfig = {
    'pool_name': 'aicall',
    'host': '172.16.0.17',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'sharedata',
    'pool_resize_boundary': 10,
    'enable_auto_resize': True,
    # 'max_pool_size': 10
}
pool = ConnectionPool(**dbConfig)

#ip = "172.16.2.2:8080"
#ip = "116.62.230.242:9044"
ip = "172.16.0.9:8080"
url1 = "http://"
url2 = "/smartdemo/smatrIvr"
phone=""

def post(postdata):
    url = "http://" + ip + "/smartdemo/smatrIvr"
    headers = {'content-type': 'charset=utf-8'}
    try:
        res = requests.post(url, data=postdata, headers = headers)
        logger.debug(res.json())
        return res.json()
        
    except Exception  as e:
        logger.debug(e)
        return ""

def get():
    url = "http://" + ip + "/smartdemo/smatrIvr?notify=enter&&charset=UTF-8"
    re = requests.get(url)
    logger.debug(re.json())

class MSG():
    phone = ""
    callid = ""
    
    def set(self, phone, callid):
        self.phone = phone
        self.callid = callid


    def enter(self):
        logger.debug("post---------enter-------------")
        logger.debug(phone)
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
        return post(indata)

    def message(self, msg, playstate):
        logger.debug("post----------asrmessage_notify------------")
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
        
        return post(indata)

    def playResult(self, data):
        logger.debug("post----------playback_result------------")
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
        
        return post(indata)

    def leave(self):
        logger.debug("post----------leave------------")
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
        logger.debug("post----------wait------------")
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
        return post(indata)

def tansContent(content):
    if len(content) == 0:
        return ""
    logger.debug(content)
    ret = ""
    for i in content:
        ltemp=i.split("/")
        file=ltemp[-2]+"/"+ltemp[-1]
        logger.debug(ltemp[-1])
        logger.debug(file)
        if len(file) > 60:
            ret = ret+getContent(file)
        else:
            ret = ret+getAIContent(file)
    logger.debug("ret:"+ret)
    return ret
        
def getContent(id):
    gsql = "SELECT content FROM tesdb001.tb_tencent_content WHERE id='"+id+"';"
    cont = ""
    with pool.cursor() as cursor:
        try:
            cursor.execute(sql)
            records = cursor.fetchall()
            for rw in records:
                cont=rw.get("content")
        except:
            logger.error("Error: unable to fetch gateway data.")
    return cont

def insertType(phone,callid, Type):
    logger.debug(phone + "---" + Type)
    gsql = "insert into tesdb001.tb_call_stat values('"+callid+"','"+phone+"',0,'"+Type+"',now())\
             ON DUPLICATE KEY UPDATE callerid='"+phone+"',type='"+Type+"';"
    logger.debug(gsql)
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
        except Exception as e:
            logger.error(e)

def deleteCallInfo(callid):
    gsql = "delete from tb_call_info where callid='%s'"%(callid)
    logger.debug(gsql)
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
        except Exception as e:
            logger.error(e)

def getMaxCruuid():
    gsql = "select max(cr_uuid)+1 uuid from sharedata.tb_callrecord;"
    cont = ""
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw.get("uuid")
        except Exception as e:
            logger.error(e)
    return cont

def getMaxTaskUUid():
    gsql = "select max(task_uuid)+1 as uuid from sharedata.tb_task;"
    cont = ""
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw.get("uuid")
        except Exception as e:
            logger.error(e)
    return cont

def getTaskStatu(taskid):
    gsql = "select CASE task_status WHEN 1 THEN '它在跑'\
            WHEN 2 THEN '它停了' \
            WHEN 10 THEN '它完了'\
            ELSE 'more' END\
            as testCol from sharedata.tb_task where task_id='%s';\
            "%(taskid)
    cont = ""
    logger.debug(gsql)
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                logger.debug(cont)
                cont=rw.get('testCol')
        except Exception as e:
            logger.error(e)
    
    logger.debug(cont)
    return cont

def getcrStatu(phone):
    gsql = "select  CASE cr_status WHEN 0 THEN '还没打,别着急'\
            WHEN 2 THEN '正在打,准备接' \
            WHEN 3 THEN '正在打,你说话' \
            WHEN 10 THEN '打完了,你懂得'\
            WHEN 11 THEN '失败了,你看着办'\
            ELSE 'more' END\
            as testCol from sharedata.tb_callrecord where cr_mobile='%s';\
            "%(phone)
    cont = ""
    logger.debug(gsql)
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                logger.debug(cont)
                cont=rw.get('testCol')
        except Exception as e:
            logger.error(e)
    logger.debug(cont)
    return cont

def getVbContent(Type):
    gsql = "select vb_uuid from sharedata.tb_verbal where vb_content = '%s';"%(Type)
    cont = ""
    logger.debug(gsql)
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw.get("vb_uuid")
        except Exception as e:
            logger.error(e)
    return cont

def insertRecord(phone, Type, mod):
    logger.debug(phone + "---" + Type)
    taskid = "TK%s"%(phone)
    cruuid = getMaxCruuid()
    taskuuid = getMaxTaskUUid()
    vbuuid = getVbContent(Type)
    crstat = 0
    taskstat = 1
    if mod == 0:
        crstat = 2
        taskstat = 10
    upsql = ""
    upsql2 = ""
    if mod == 1:
        upsql = "delete from  sharedata.tb_callrecord where cr_taskid='%s'\
            "%(taskid)

        upsql2 = "delete from  sharedata.tb_callrecord where cr_mobile='%s'\
            "%(phone)

    crsql = "INSERT INTO sharedata.tb_callrecord \
            VALUES (%d , '%s', 'user0001', NULL ,NULL , '%s', %d, now(3), 0, 0, NULL, NULL, NULL, NULL, '0', '0')\
            ;"%(int(cruuid), taskid, phone, crstat)

    tasksql = "INSERT INTO sharedata.tb_task \
                VALUES (%d , '%s', 'user0001', 'aaa',null, 'aaa', null,null, %d, '2', '2', '2', '[00:00-03:00];',\
                'GOIP', 'GW00002', '%s',null, '7777', 45)\
                ON DUPLICATE KEY UPDATE task_verbal='%s', task_status = %d;\
                "%(int(taskuuid), taskid, taskstat, vbuuid, vbuuid, taskstat)

    logger.debug(crsql)
    logger.debug(tasksql)
    with pool.cursor() as cursor:
        try:
            if mod == 1:
                cursor.execute(upsql)
                cursor.execute(upsql2)
            cursor.execute(crsql)
            cursor.execute(tasksql)
        except Exception as e:
            logger.error(e)

def getAsrdetail(phone):
    gsql = "SELECT cr_asrdetail FROM sharedata.tb_callrecord WHERE cr_mobile='%s';\
            "%(phone)
    cont = ""
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw.get("cr_asrdetail")
        except Exception as e:
            logger.error(e)
    return cont

def getAIContent(id):
    gsql = "SELECT content FROM tesdb001.tb_ai_content WHERE id='"+id+"';"
    cont = ""
    with pool.cursor() as cursor:
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                cont=rw.get("content")
        except Exception as e:
            logger.error(e)
    return cont

class myWind(QWidget):
    msg = MSG()
    
    def __init__(self, mom):
        self.mom = mom
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
        self.linePhone.returnPressed.connect(self.msgEnter)

        #lineedit
        self.lineMsg = QLineEdit(self)
        self.lineMsg.move(20, 490)
        self.lineMsg.resize(200, 20)
        self.lineMsg.returnPressed.connect(self.msgMsg)

        #lineedit
        self.lineType = QLineEdit(self)
        self.lineType.move(100, 522)
        self.lineType.resize(120, 20)
        self.lineType.setText("股票呼叫系统黄婷")

        
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
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "确定退出？",
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.msg.leave()
            self.mom.show()
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
        Type=self.lineType.text()
        if len(phone) == 0 :
            reply = QMessageBox.question(self, '提示', "没有电话号码",
                                     QMessageBox.Yes, QMessageBox.Yes)
            return
        self.textbox.moveCursor(QTextCursor.End)
        callid = "2c4146f8-6afe-11e8-8cb2-" + phone
        self.msg.set(phone, callid)
        logger.debug(phone)
        deleteCallInfo(callid)
        insertRecord(self.msg.phone, Type, 0)
        res = self.msg.enter()
        self.msgAnalysis(res)
        self.btn.setEnabled(True)
        self.btnEnter.setEnabled(False)
        self.btnMsg.setEnabled(True)
        self.btnleav1.setEnabled(True)

    def msgAnalysis(self, res):
        if isinstance(res, str):
            return
        logger.debug("actrion:" + res["action"])
        if res["action"] == 'playback':
            txt = "机器人:" + tansContent(res["params"]["prompt"])
            self.textbox.append(txt)
            time.sleep(1)
            resPr = self.msg.playResult("") 
            self.msgAnalysis(resPr)
        elif res["action"] == 'wait':
            timeout = int(res["params"]["timeout"])
            if timeout < 1000:
                res = self.msg.wait()
                self. msgAnalysis(res)
            else:
                return
        elif res["action"] == 'hangup':
            self.msgLeave()

    def msgLeave(self):
        self.msg.leave()
        self.btn.setEnabled(False)
        self.btnEnter.setEnabled(True)
        self.btnMsg.setEnabled(False)
        self.btnleav1.setEnabled(False)

    def msgWait(self):
        res = self.msg.wait()
        self. msgAnalysis(res)
        
    def msgMsg(self):
        self.textbox.moveCursor(QTextCursor.End)
        if len(self.lineMsg.text()) == 0 :
            reply = QMessageBox.question(self, '提示', "内容为空",
                                     QMessageBox.Yes, QMessageBox.Yes)
            return
        content = "用户  :" + self.lineMsg.text()
        self.textbox.append(content)
        res = self.msg.message(self.lineMsg.text(), "false")
        self.msgAnalysis(res)
        self.lineMsg.setText("")

    def reset(self):
        self.textbox.setText("")
        #self.linePhone.setText("")

class myDialWind(QWidget):

    def __init__(self, mom):
        self.mom = mom
        super().__init__()
        self.initUI()
        
    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        
        #label
        self.lblPhone = QLabel(self)
        self.lblPhone.setText("这个号码")
        self.lblPhone.move(23, 50)

        #lineedit
        self.linePhone = QLineEdit(self)
        self.linePhone.move(100,50)
        self.linePhone.resize(120, 20)

        #label
        self.lblVB = QLabel(self)
        self.lblVB.setText("什么话术")
        self.lblVB.move(23, 100)
        
        #lineedit
        self.lineVB = QLineEdit(self)
        self.lineVB.move(100,100)
        self.lineVB.resize(120, 20)
        self.lineVB.setText("股票呼叫系统黄婷")

        #button
        self.btnReset = QPushButton('开打！', self)
        self.btnReset.clicked.connect(lambda:self.dial())
        self.btnReset.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnReset.resize(self.btnReset.sizeHint())
        self.btnReset.move(200,150)

        #button
        self.btnshow = QPushButton('说的啥', self)
        self.btnshow.clicked.connect(lambda:self.showasr())
        self.btnshow.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnshow.resize(self.btnReset.sizeHint())
        self.btnshow.move(110,150)

        #button
        self.btnisdial = QPushButton('打了吗', self)
        self.btnisdial.clicked.connect(lambda:self.isdial())
        self.btnisdial.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnisdial.resize(self.btnReset.sizeHint())
        self.btnisdial.move(23,150)

        #Widget
        self.setGeometry(500,700,700,520)
        self.setWindowTitle('CSmaintes')
        self.setWindowIcon(QIcon('ai.png'))
        self.resize(350, 200)
        #self.move(300, 300) 位置
        self.center()

    def check(self):
        if len(self.linePhone.text()) == 0 :
            reply = QMessageBox.question(self, '提示', "号码为空",
                                     QMessageBox.Yes, QMessageBox.Yes)
            return False
        return True

    def dial(self):
        if not self.check() :
            return
        phone = self.linePhone.text()
        Type = self.lineVB.text()
        insertRecord(phone, Type, 1)

    def isdial(self):
        if not self.check() :
            return
        phone = self.linePhone.text()
        taskid = "TK%s"%(phone)
        task_status = getTaskStatu(taskid)
        cr_status = getcrStatu(phone)
        msg = "任务:%s\n电话:%s"%(task_status, cr_status)
        QMessageBox.information(self,
                                    "消息框标题",  
                                    msg,  
                                    QMessageBox.Yes )

    def showasr(self):
        if not self.check() :
            return
        phone = self.linePhone.text()
        msg = getAsrdetail(phone)
        QMessageBox.information(self,
                                    "消息框标题",  
                                    msg,  
                                    QMessageBox.Yes)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "确定退出？",
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.mom.show()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class myMainWind(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.txtwin = myWind(self)
        self.dialwin = myDialWind(self)

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        
        #button
        self.btn = QPushButton('文字电话', self)
        self.btn.clicked.connect(lambda:self.mywinshow())
        self.btn.setToolTip('This is a <b>QPushButton</b> widget')
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(230,100)

        self.btnReset = QPushButton('真打电话', self)
        self.btnReset.clicked.connect(lambda:self.dialwinshow())
        self.btnReset.setToolTip('This is a <b>QPushButton</b> widget')
        self.btnReset.resize(self.btnReset.sizeHint())
        self.btnReset.move(20,100)

        #Widget
        self.setGeometry(500,700,700,520)
        self.setWindowTitle('CSmaintes')
        self.setWindowIcon(QIcon('ai.png'))
        self.resize(350, 200)
        #self.move(300, 300) 位置
        self.center()
        self.show()
    
    def mywinshow(self):
        self.txtwin.show()
        self.hide()

    def dialwinshow(self):
        self.dialwin.show()
        self.hide()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def mainwin():
    app = QApplication(sys.argv)
    w = myMainWind()
    sys.exit(app.exec_())

def main():
    #CStes()
    mainwin()

if __name__ == '__main__':
    main()
