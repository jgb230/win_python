#!/bin/python
#coding=utf-8
import threading
from threading import Thread, Condition
from time import ctime,sleep
import socket
import json
import time
import hashlib


class utl:
    def __init__(self, version, magic):
        self.version = version
        self.magic = magic

    def head(self, len, commond):
        head = []
        head.extend(self.int2bytes(len))
        head.extend(self.int2bytes(0))
        head.extend(self.short2bytes(commond))
        head.extend(self.char2bytes(self.version))
        head.extend(self.magic)
        head.extend(self.short2bytes(0))
        print("==============",head)
        return head

    def int2bytes(self, num):
        bs = []
        bs.append(num>>0 & 0xff)
        bs.append(num>>8 & 0xff)
        bs.append(num>>16 & 0xff)
        bs.append(num>>24 & 0xff)
        return bs

    def short2bytes(self, num):
        bs = []
        bs.append(num>>0 & 0xff)
        bs.append(num>>8 & 0xff)
        return bs

    def char2bytes(self, b):
        bs = []
        bs.append(b>>0 & 0xff)
        return bs

    def bytes2int(self, bs):
        return (
                (bs[3]&0xff)<<24
                | (bs[2]&0xff)<<16
                | (bs[1]&0xff)<<8
                | (bs[0]&0xff))


    def bytes2short(self, bs):
        return ((bs[1]&0xff)<<8
                | (bs[0]&0xff))


