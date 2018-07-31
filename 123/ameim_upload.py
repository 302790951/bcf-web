#!/usr/bin/env python
#coding=utf8

#大文件上传

import sys
import httplib
import urllib
import json
import time
import hmac
import base64
import hashlib
import traceback
import os

#秘钥
AK = "ak_cyp"
SK = "72606dcfae72d81defdc6c91b742e892ea71ee5c"
BUCKET_NAME = "ameim"

#块大小
PACK_SIZE = 2 * 1024 * 1024

#大文件的MD5值
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

#
def get_file_size(file_path, file_name):
    fsize = os.path.getsize(file_path+file_name)
    return fsize

#
def get_filename_digest(bucketname, filename):
    content = str(bucketname) + '/' + str(filename)
    hashing = hashlib.sha1(content).hexdigest()
    return str(hashing)

#授权
def get_authorization(method, file_name, overdue_sec = 0):
    try:
        global AK
        global SK
        global BUCKET_NAME
        expires = str(int(time.time()) + overdue_sec)
        name = '{0}\n{1}\n{2}\n{3}\n'.format(method, BUCKET_NAME, file_name, expires)
        hashing = base64.urlsafe_b64encode(hmac.new(SK, name, hashlib.sha1).digest())
        authorization = AK + ':' + hashing + ':' + expires
        return authorization
    except Exception, e:
        #log
        pass

#上传初始化
def upload_file_init(file_name):
    try:
        global BUCKET_NAME
        http_client = None
        host = "{0}.bs2ul.yy.com".format(BUCKET_NAME)
        http_client = httplib.HTTPConnection(host)
        if http_client is None:
            print 'HTTPConnection failed'
            #log
            return None

        method = "POST"
        url = "/{0}?uploads".format(file_name)
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime())
        authorization = get_authorization(method, file_name)
        params = ''
        headers = {
            "Date":date, \
            "Authorization":authorization
            }
        http_client.request(method, url, params, headers)
        response = http_client.getresponse()
        status = response.status
        body = response.read()
        if status is not 200:
            print body
            return None

        data = json.loads(body)
        zone = data["zone"]
        uploadid = data["uploadid"]
        http_client.close()

        result = {}
        result["uploadid"] = uploadid
        result["zone"] = zone
        return result
    except Exception, e:
        #log
        pass


#分快上传
def upload_file_block(file_path, file_name, uploadid, zone, up_name):
    try:
        global BUCKET_NAME    
        http_client = None
        partnumber = 0
        host = zone
        method = "PUT"
        #host = "{0}.{1}.bs2ul.yy.com".format(BUCKET_NAME, zone)
        #print host
        #host='60.214.170.217'
        http_client = httplib.HTTPConnection(host)
        if http_client is None:
            return None

        with open(file_path+file_name, 'rb') as fp:
            while True:
                data = fp.read(PACK_SIZE)
                if 0 == len(data):
                    fp.close()
                    break
                date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime())
                authorization = get_authorization(method, up_name)
                headers = {
                    "Date":date, \
                    "Authorization":authorization, \
                    "Host":zone
                }
                url = "/{0}?partnumber={1}&uploadid={2}".format(up_name, partnumber, uploadid)
                params = data
                print method, url
                http_client.request(method, url, params, headers)
                response = http_client.getresponse()
                status = response.status
                body = response.read()
                print status
                if status is not 200:
                    return None

                partnumber += 1

            #返回分片数
            if 0 == partnumber:
                return None
            return partnumber

    except Exception, e:
        print traceback.format_exc().replace('\n',' \\n ')
        pass


#分快上传完成
def upload_file_complete(file_path, file_name, uploadid, zone, partnumber, up_name):
    try:
        global BUCKET_NAME
        http_client = None
        host = zone
        #host='112.91.19.35'
        #host = "{0}.{1}.bs2ul.yy.com".format(BUCKET_NAME, zone)
        #print host
        http_client = httplib.HTTPConnection(host)
        if http_client is None:
            #log
            return None

        method = "POST"
        url = "/{0}?uploadid={1}".format(up_name, uploadid)
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime())
        authorization = get_authorization(method, up_name)
        length = get_file_size(file_path, file_name)
        #print length
        '''headers = {
            "Date":date, \
            "Authorization":authorization, \
            "Host":zone,\
            "Content-Type":"image/jpeg",\
            "Content-Length":length
        }'''
        headers = {
            "Date":date, \
            "Authorization":authorization, \
            "Host":zone
        }
        body = {}
        body["partcount"] = partnumber
        params = json.dumps(body)
        print method, url, params

        http_client.request(method, url, params, headers)
        response = http_client.getresponse()
        status = response.status
        body = response.read()

        print status
        if status is not 200:
            #log
            return None

        return True
    except Exception, e:
        print traceback.format_exc().replace('\n',' \\n ')
        pass

#上传大文件
#file_path 文件绝对路径 /var/log/log.txt
#file_name 文件名 log.txt
def upload_file(file_path, file_name, up_name):
    try:
        global BUCKET_NAME

        result = upload_file_init(up_name)
        if result is None:
            print "upload_file_init failed"
            return None
        uploadid = result["uploadid"]
        zone = result["zone"]
        print "upload_file_init success"
        print "BUCKET_NAME: ", BUCKET_NAME
        print "file_path: ", file_path
        print "file_name: ", up_name
        print "zone: ", zone
        print "uploadid: ", uploadid
        #上传
        partnumber = upload_file_block(file_path, file_name, uploadid, zone, up_name)
        if partnumber is None:
            print "upload_file_block failed"
            return None
        print "upload_file_block success" 

        #上传完成
        result = upload_file_complete(file_path, file_name, uploadid, zone, partnumber, up_name)
        if result is None:
            print "upload_file_complete failed"
            return None
        print "upload_file_complete success"
        return True

    except Exception, e:
        print traceback.format_exc()
        pass


if __name__ == "__main__":
    fullname = sys.argv[1]
    upname = sys.argv[2]
    pos = fullname.rfind("/")
    pos_win = fullname.rfind("\\")
    if pos < 0 and pos_win < 0:
        filepath = ""
        filename = fullname
    elif pos >= 0:
        filepath = fullname[:pos+1]
        filename = fullname[pos+1:]
    elif pos_win >= 0:
        filepath = fullname[:pos_win+1]
        filename = fullname[pos_win+1:]
    #print filepath, filename
    upload_file(filepath, filename, upname)

