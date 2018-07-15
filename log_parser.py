# -*- coding: utf-8 -*-

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os,re
import time
from urllib.parse import urlparse
import mysql.connector

# init *******
target_file = "/var/log/nginx/"
pos = 0
i = 0
rows = 0
instances={}
pos_file = ''

url = urlparse('mysql://user:pass@localhost:3306/nginx')

conn = mysql.connector.connect(
    host = url.hostname or 'localhost',
    port = 3306,
    user = 'root',
    password = '',
    database = url.path[1:],
)
tabel = 'access_log'
conn.ping(reconnect=True)
cur = conn.cursor(dictionary=True)
# init *******

def init_val(file):
	global i,pos_file
	pos_file = file+'.pos'
	try:
		fp = open(pos_file,'r')
		line = fp.readline()
		if line =='':
			i = 0
		else:
			i = int(line)
		fp.close()
	except:
		i = 0
def update_val():
	fp = open(pos_file,'w+')
	fp.write(str(i))
	fp.close()

def is_divided(uri):
    if re.search("/.*?uploadId=.*/",uri) is None:
        return False
    else:
        return True

def is_ended(method,uri):
    return method == "POST" #分割アップロードはPOSTで終わる

def router(elements):
    global instances,i,rows
    if is_divided(elements['request']):
        uid = elements['request'].split("?uploadId=",1)[1] #******
        uid = uid[0:32]
        print('request',elements['request'],'uid',uid,' ended?',is_ended(elements['request_method'],elements['request']),' keys:',instances.keys())
        if is_ended(elements['request_method'],elements['request']) :
            #　POSTがくるか、フィアルの終端まで来た場合は、DBにインサートする。ただし、DBに既に同じUIDが登録されていないかチェックする。登録されていた場合は、そのレコードに加算する形でアップロード。
            if uid in instances.keys(): # インスタンスが既に存在する場合
                insert_DB(instances[uid].show_elements()) #インスタンスの中身をすべて取得し、そのままインサート
                del instances[uid]
#            else:
#                insert_DB(elements)
        else:
#            if i == rows :
#                for uid in instances.keys():
#                    insert_DB(instances[uid].show_elements())
#                    del instances[uid]
#                return
            if uid in instances.keys(): # インスタンスが既に存在する場合
                instances[uid].merge(elements['request_length'])
            else:
                instances[uid] = DividedFiles(elements)
            # 分割アップロードのファイルが来た場合は、最後のPOSTがくるまで待つ。

    else:
        insert_DB(elements)
        #　分割アップロードでない場合は、そのままインサートする

def parser(line):
    dict={}
    for v in line.split('\t'):
        k,v = v.split(':',1)
        dict[k]=v
    return dict

def tail(file):
    #前回読んだファイルの行数からファイルの最後まで読み込む
    global rows,i,pos
    rows = sum(1 for line in open(file))
    init_val(file)
    fp=open(file,'r')
    for line in fp.readlines()[i+1: rows]:
        router(parser(line))
        i+=1
        update_val()
    pos = rows-1  # 読み込んだ行数を更新

def is_dict(path):
   arr = path.split("/")
   return arr[-1] == ""

def insert_DB(elements):
    if is_dict(elements['uri']):
        return
    keys =''
    values =''
    for k,v in elements.items():
       keys = keys + ',' + k
       values = values + ',"' + v +'"'
    keys = keys.split(',',1)[1]
    values = values.split(',',1)[1]
    try:
       cur.execute('INSERT INTO {}({}) VALUES({})'.format(tabel,keys,values))
       conn.commit()
    except:
       print('insert error')
       conn.rollback()
       raise


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        #time.sleep(200)
        print('Event',event)
        if event.is_directory:
            return
        # ファイルが変更された時に、ファイル読み込みを行う
        if event.src_path == "/var/log/nginx/ring.access.log":
            tail(event.src_path)


class DividedFiles:
    def __init__(self, elements):
        self.elements = elements

    def merge(self,length):
        #print('before merge',self.elements)
        self.elements['request_length']=str(int(self.elements['request_length']) + int(length))
        #print('after merge',self.elements)
        return

    def show_elements(self):
        #print('instances',elements)
        return self.elements

def main():
    while 1:
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, target_file, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(500)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ in '__main__':
    main()
