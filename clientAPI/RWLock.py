#!/bin/python
#coding=utf-8
import threading

class RWLock:
    def __init__(self):
        self.m_lock = threading.Lock()
        self.m_rcond = threading.Condition(self.m_lock)
        self.m_wcond = threading.Condition(self.m_lock)
        self.read_cnt = 0  # 等待获取读锁的线程数
        self.write_cnt = 0  # 等待获取写锁的线程数
        self.inwriteflag = False

    def lock_read(self):
        self.m_lock.acquire()
        while (self.write_cnt != 0):
            self.m_rcond.wait()
        
        self.read_cnt = self.read_cnt + 1
        self.m_lock.release()
    
    
    def lock_write(self) :
        self.m_lock.acquire()
        self.write_cnt = self.write_cnt + 1
        while(self.read_cnt != 0 or self.inwriteflag):
            self.m_wcond.wait()
        
        self.inwriteflag = True
        self.m_lock.release()
    
    def release_read(self):
        self.m_lock.acquire()
        self.read_cnt = self.read_cnt - 1
        if (self.read_cnt == 0 and self.write_cnt > 0):
            self.m_wcond.notify()
        self.m_lock.release()
    
    def release_write(self):
        self.m_lock.acquire()
        self.write_cnt = self.write_cnt - 1
        if (self.write_cnt == 0):
            self.m_rcond.notifyAll()
        else:
            self.m_wcond.notify()
        self.inwriteflag = False
        self.m_lock.release()
    


