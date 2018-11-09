#!/usr/bin/python3
# coding=utf-8

import paramiko
import os

phonelist = ["18534976037",
"18855579562",
"13665758701",
"15774771141",
"18144233632",
"18178362186",
"15200975925"]

def sftp_upload(host,port,username,password,local,remote):
    sf = paramiko.Transport((host,port))
    sf.connect(username = username,password = password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):#判断本地参数是目录还是文件
            for f in os.listdir(local):#遍历本地目录
                sftp.put(os.path.join(local+f),os.path.join(remote+f))#上传目录中的文件
        else:
            sftp.put(local,remote)#上传文件
    except :
        print('upload exception:')
    sf.close()

def sftp_download(host,port,username,password,local,remote):
    sf = paramiko.Transport((host,port))
    sf.connect(username = username,password = password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):#判断本地参数是目录还是文件
            for f in sftp.listdir(remote):#遍历远程目录
                 sftp.get(os.path.join(remote+f),os.path.join(local+f))#下载目录中文件
        else:
            sftp.get(remote,local)#下载文件
    except Exception as e:
        print('download exception:',e)
    sf.close()
    
if __name__ == '__main__':
    host = '121.196.204.197'#主机
    port = 22 #端口
    username = 'root' #用户名
    password = 'Galaxyeye01' #密码
    #本地文件或目录，与远程一致，当前为windows目录格式，window目录中间需要使用双斜线
    for v in phonelist:
        local = 'E:\\record\\%s.wav'%(v)
        print(local)
        remote = '/usr/local/freeswitch/recordings/\*/%s\*.wav'%(v)
        #远程文件或目录，与本地一致，当前为linux目录格式
        print(remote)
        sftp_download(host,port,username,password,local,remote)#下载
