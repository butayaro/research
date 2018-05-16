##input.py

from collections import Counter
import sys, json, numpy as np
from scipy.sparse import lil_matrix, csr_matrix
#import TestModel
sys.path.append('/home/r_irie/jstest/libsvm-3.22/tools')
sys.path.append("/home/r_irie/jstest/libsvm-3.22/python/")
#import svm2
from urllib.parse import urlparse
import mysql.connector
import math
import datetime

threshold=30

url = urlparse('mysql://user:pass@localhost:3306/niconico')

conn = mysql.connector.connect(
    host = url.hostname or 'localhost',
    port = 3306,
    user = 'root',
    password = '',
    database = url.path[1:],
)
conn.ping(reconnect=True)
cur = conn.cursor(dictionary=True)
#cur = conn.cursor()

def return_match_index(key,i,dict):
    for element in dict:
        if key == element:
             index = dict[key]
             return index

def create_input(year,month):
    f = open('ext-dict-1236.json','r')
    ext_dict = json.load(f)
    f = open('usr-dict.json','r')
    usr_dict = json.load(f)

    ym = year+'-'+month

    cycle = 31; #in case classification cycle is 30day
    zero = ym +'-'+str(math.ceil(cycle/4*0)+1)
    first = ym +'-'+str(math.ceil(cycle/4*1))
    second = ym +'-'+str(math.ceil(cycle/4*2))
    third = ym +'-'+str(math.ceil(cycle/4*3))
    forth = ym +'-'+str(math.ceil(cycle/4*4))

    #cur.execute('select time,source,size,uri,count(time between "'+zero+' 00:00:00" and "'+first+' 00:00:00" or null) first ,count(time between "'+first+' 00:00:01" and "'+second+' 00:00:00" or null) second,count(time between "'+second+' 00:00:01" and "'+third+' 00:00:00" or null) third,count(time between "'+third+' 00:00:01" and "'+forth+' 00:00:00" or null) forth from (select substring_index(substring_index(uri,".",1),"=",-1) vid,from_unixtime(unixtime) time,source,uri,size from niconico.201509 where from_unixtime(unixtime) "'+zero+' 00:00:00" and "'+forth+' 00:00:00") as A group by vid'))

    sql_query='select vid,time,source,size,uri,count(time between "{} 00:00:00" and "{} 00:00:00" or null) first ,count(time between "{} 00:00:01" and "{} 00:00:00" or null) second,count(time between "{} 00:00:01" and "{} 00:00:00" or null) third,count(time between "{} 00:00:01" and "{} 00:00:00" or null) forth from (select substring_index(substring_index(uri,".",1),"=",-1) vid,from_unixtime(unixtime) time,source,uri,size from niconico.201509 where from_unixtime(unixtime) between "{} 00:00:00" and "{} 00:00:00") as A group by vid'.format(zero,first,first,second,second,third,third,forth,zero,forth)
#    print(sql_query)

    cur.execute(sql_query)
    lines = cur.fetchall()
    i = 0
    row = len(lines)
    max = len(ext_dict)
    ext_arr = lil_matrix((row,max))
    max = len(usr_dict)
    usr_arr = lil_matrix((row,max))
    size_list,c1_list,c2_list,c3_list,c4_list,fi_list,y_list=[],[],[],[],[],[],[]
    zero_labels = []
    for temp in lines:
        uri = temp['vid']
        size = temp['size']
        ext = uri.rsplit('.',1)
        usr = temp['source']
        c1 = temp['first']
        c2 = temp['second']
        c3 = temp['third']
        c4 = temp['forth']
        time = temp['time']


        #print("strat",datetime.datetime.now())
        cur.execute('select time from niconico.20150910 where vid = %s and time between (%s + interval 1 second) and (%s + interval %s day)',(uri,time,time,threshold))

        if len(cur.fetchall()) > 0:
            #(select substring_index(substring_index(uri,".",1),"=",-1) vid,from_unixtime(unixtime) time,source,uri,size from niconico.201509 where from_unixtime(unixtime) "'+zero+' 00:00:00" and "'+forth+' 00:00:00") as A
            label = 1
        else:
            print(uri)
            zero_labels.append(uri)
            label = 0
        #print("ex end",datetime.datetime.now())
        if len(ext) > 1:
             ext = ext[1]
        else :
             ext = ""

        #print("start",datetime.datetime.now())
        index = return_match_index(ext,i,ext_dict)
        if index != None:
             ext_arr[i,index] = 1

        index = return_match_index(usr,i,usr_dict)
        if index != None:
             usr_arr[i,index] = 1
        #print("lil end",datetime.datetime.now())

        y_list.append(label)
        size_list.append(size)
        c1_list.append(c1)
        c2_list.append(c2)
        c3_list.append(c3)
        c4_list.append(c4)
        fi_list.append(uri)
        i+=1

    np.save('zero-labels-'+year+month+'.npy',np.array(zero_labels))
    #"""
    y_arr = np.array(y_list)
    s_arr = np.array(size_list)
    c1_arr = np.array(c1_list)
    c2_arr = np.array(c2_list)
    c3_arr = np.array(c3_list)
    c4_arr = np.array(c4_list)
    #fi_arr = np.array(fi_list)

    #X = ext_arr
    X = ext_arr.tocsr().todense()
    usr = usr_arr.tocsr().todense()
    #usr = usr_arr
    X = np.c_[X,usr]
    X = np.c_[X,s_arr]
    X = np.c_[X,c1_arr]
    X = np.c_[X,c2_arr]
    X = np.c_[X,c3_arr]
    X = np.c_[X,c4_arr]

    np.savez('Input-'+year+month+'.npz',  data=X)
    np.save('label-'+year+month+'.npy',y_arr)
    return X,fi_list,size_list

def main():
    f = open('ext-dict-1236.json','r')
    ext_dict = json.load(f)
    f = open('usr-dict.json','r')
    usr_dict = json.load(f)
    X,files,size_list = create_input("2015","12")
    #np.savez('Input-test.npz',  data=X)
    # DNN = TestModel.test_model(X,'model.h5')
    # SVM = svm2.testing(X,'libsvm.model')
    # i = 0
    # while(i < len(DNN) ):
    #    total = float(DNN[i])+float(SVM[i][1])
    #    try:
    #       cur.execute('INSERT INTO score(uri,DNN,SVM,Size,UserRank,User,Total) VALUES(%s,%s,%s,%s,%s,%s,%s) on duplicate key update uri=%s,DNN=%s,SVM=%s,Size=%s,UserRank=%s,User=%s,Total=%s', (files[i],float(DNN[i]),float(SVM[i][1]),size_list[i],0,"test-user",total,files[i],float(DNN[i]),float(SVM[i][1]),size_list[i],0,'test-user',total))
    #       conn.commit()
    #    except:
    #       conn.rollback()
    #       raise
    #    i+=1
    #
    # hot_quota = 2000
    # cur.execute('set @csum := 0')
    # cur.execute('select uri from (select *,(@csum := @csum + Size) as cumulative_sum from score order by Total DESC ) as A where cumulative_sum > %s',[hot_quota])
    # f = open('cold-files','w')
    # results = cur.fetchall()
    # for file in results:
    #     f.writelines(file['uri']+'\n')
    # f.close()
    #print(results)

#start process
if __name__ == '__main__':
    main()
