
#!/usr/bin/env python3
# coding=utf-8
import ssl
import json
import requests
import time
import random
import hashlib
from urllib import parse

hl = hashlib.md5()

ip = "172.16.2.44:8080"
#ip = "116.62.230.242:9044"
#ip = "172.16.0.10:8080"


def post(postdata):
    url = "http://" + ip + "/smartdemo/smatrIvr"
    headers = {'content-type': 'charset=utf-8'}
    res = requests.post(url, data=postdata, headers = headers)
    print(res.status_code)
    print(res.url)
    print(res.text)
    print(res.json()['params']['prompt'])

def get():
    url = "http://" + ip + "/smartdemo/smatrIvr?notify=enter&&charset=UTF-8"
    re = requests.get(url)
    print(re.json())

def ttsget(ttsdata):
    url = "https://api.ai.qq.com/fcgi-bin/aai/aai_tts"
    #url = 'http://httpbin.org/get'
    headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8'}
    res = requests.get(url, params=ttsdata, headers = headers)
    print(res.status_code)
    print(res.url)
    print(res.text)

def ttspost(ttsdata):
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://api.ai.qq.com/fcgi-bin/aai/aai_tts"
    #url = 'http://httpbin.org/post'
    headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8'}
    res = requests.post(url, data=ttsdata, headers = headers)
    print(res.status_code)
    print(res.url)
    print(res.text)

def getReqSign(data, appKey):
    keys = sorted(data)
    signstr = ''
    for key in keys:
        signstr = signstr + key + '=' + parse.quote(str(data[key])) + '&'
    signstr = signstr + 'app_key=' + appKey
    print(signstr)
    hl.update(signstr.encode(encoding='utf-8'))
    return hl.hexdigest().upper()

def getdata(data):
    signstr = ''
    for key in data:
        value=''
        if isinstance(data[key],str):
            value=data[key]
        else:
            value=str(data[key])
        signstr = signstr + key + '=' + value + '&'
    leng=len(signstr)
    return signstr[0:leng-1]
    
def main():

    print("post---------asr-------------")
    indata='''
            {
            "calleeid":"17794589041",
            "callerid":"8888",
            "callid":"1fe74812-e376-4319-b335-3de1b494325d",
            "errorcode":0,
            "flowdata":"abc",
            "flowid":"abc",
            "notify":"enter"
            }
            '''.encode('utf-8')
    post(indata)

    print("post---------tts-------------")
    times=int(time.time())
    print(times)
    rands=str(int(random.random()*1000000))
    print(rands)
    text = '你好'.encode('utf-8')
    data={'app_id':1106844169,
          'speaker':2,
          'format':2,
          'volume':0,
          'speed':100,
          'text':text,
          'aht':0,
          'apc':58, 
          'time_stamp':times,
          'nonce_str':'fa577ce340859f9fe',
          'sign':'953EE4AFDA166C5C4D5D3BFB5885C57E'}
    #print(str(data))
    #data['sign']=getReqSign(data, 'MbR3PDlBdAv3wH9d')
    
    #print(data)
    #print(getdata(data))
    #ttspost(data)

    
if __name__ == '__main__':
    main()
