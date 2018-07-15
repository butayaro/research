#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import json
import codecs
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from pymongo import MongoClient
import os,sys,subprocess,collections
import boto3	

def get_extension_group(extension):
	audio=['.aif','.cda','.mid','.mp3','.midi','.mpa','.ogg','.wav','.wma','.wpl']
	compressed=['.7z','.arj','.deb','.pkg','.rar','.rpm','.gz','.z','.zip','.cab','.dmg','.lz']
	disc=['.bin','.dmg','.iso','.toast','.vcd','.img']
	data=['.csv','.dat','.db','.dbf','.log','.mdb','.sav','.sql','.tar','.xml','.xls','.xlsx','.xlr','.ods']
	executable=['.apk','.bat','.bin','cgi.','.pl','.com','.exe','.gadget','.jar','.py','.wsf','.dcu']
	font=['.fnt','.fon','.otf','.ttf']
	image=['.ai','.bmp','.gif','.ico','.jpeg','.jpg','.png','.ps','.psd','.svg','.tif','.tiff']
	internet=['.asp','.aspx','.cer','.cfm','.css','.htm','.html','.js','.jsp','.part','.php','.rss','.xhtml']
	presentation=['.key','.odp','.pps','.ppt','.pptx','.pot']
	program=['.c','.class','.cpp','.cs','.h','.java','.sh','.swift','.vb','.m','.pas','.hpp']
	system=['.bak','.cab','.cfg','.cpl','.cur','.dll','.dmp','.drv','.icns','.ico','.ini','.lnk','.msi','.sys','.tmp']
	video=['.3gs','.3gp','.avi','.flv','.h264','.m4v','.mkv','.mov','.mp4','.mpg','.mpeg','.rm','.swf','.vob','.wmv']
	word=['.doc','.docx','.odt','.pdf','.rtf','.tex','.txt','.wks','.wps','.wpd']	

	if extension in audio:
		 return 'audio'
	if extension in compressed:
		 return 'compressed'
	if extension in disc:
		 return 'disc'
	if extension in data:
		 return 'data'
	if extension in executable:
		 return 'executable'
	if extension in font:
		 return 'font'
	if extension in image:
		 return 'image'
	if extension in internet:
		 return 'internet'
	if extension in presentation:
		 return 'presentation'
	if extension in program:
		 return 'program'
	if extension in system:
		 return 'system'
	if extension in video:
		 return 'video'
	if extension in word:
		 return 'word'
	else: 
		return extension

def input():
    args = sys.argv
    argv = len(args)
    if argv == 4:
       Min = int(args[1])
       Max = int(args[2])
       duration = int(args[3])
    else:
       print("please input min day ")
       Min = int(input())
       print("please input duration of prediction ")
       duration = int(input())
       Max = Min + duratio
    return Min,Max,duration

def isPathExist(path):
	if os.path.exists(path) == False:
		os.makedirs(os.getcwd()+path)
	return	

def createDummyFile(full_path,size,*args):
        path,file_name = full_path.rsplit('/',1)
        isPathExist(path)
        full_path = os.getcwd()+full_path
        args=['fallocate','-l',str(size),full_path]
        #args=['truncate','-s',str(size),file_name]
        #print("path:{},size:{}".format(full_path,size))
        try:
            res = subprocess.call(args)
        except:
            print('Exception occured in making {}!!'.format(file_name))

def uploadFile(full_path,*args):
	path,file_name = full_path.rsplit('/',1)
	bucket = "demo"
#	s3 = boto3.resource('s3',endpoint_url='http://210.156.3.168:6080')
#	s3 = boto3.resource('s3',endpoint_url='http://133.1.74.32:6080')
	#bucket = s3.Bucket(bucket)
	#bucket.upload_file(file_name,file_name)


if __name__ == "__main__":
    target="China-all-utf8-2"
    mongo_client = MongoClient('localhost:27017')
    db = mongo_client[target]
    db = db["prefs"]
    # データを取得する
    i = 0
    for temp in db.find({},no_cursor_timeout=True):
        if i>10:
            break
        createDummyFile(temp['path'],temp['size'])
        uploadFile(temp['path'])
        i+=1

