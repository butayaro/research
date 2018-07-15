##input.py

from collections import Counter
import sys, json, numpy as np
from scipy.sparse import lil_matrix, csr_matrix
import TestModel
sys.path.append('/home/r-irie/Downloads/libsvm-3.22/tools')
sys.path.append("/home/r-irie/Downloads/libsvm-3.22/python/")
import svm3
from urllib.parse import urlparse
import mysql.connector
import time

normalize_size =  17940408164
url = urlparse('mysql://user:pass@localhost:3306/nginx')

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

#Read data from stdin
def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def return_match_index(key,i,dict):
    for element in dict:
        if key == element:
             index = dict[key]
             return index

def create_input(ext_dict,usr_dict):
    #get our data as an array from read_in()
    lines = read_in()
    i = 0
    row = len(lines)
    max = len(ext_dict)
    ext_arr = lil_matrix((row,max))
    max = len(usr_dict)
    usr_arr = lil_matrix((row,max))
    size_list,c1_list,c2_list,c3_list,c4_list,fi_list=[],[],[],[],[],[]
    for temp in lines:
#        print(temp)
        uri = temp['uri']
        size = temp['size'] / normalize_size
        ext = uri.rsplit('.',1)
        usr = temp['remote_addr']
        c1 = temp['first'] / 20
        c2 = temp['second'] /20
        c3 = temp['third'] /20
        c4 = temp['forth'] /20
        if len(ext) > 1:
             ext = ext[1]
        else :
             ext = ""

        index = return_match_index(ext,i,ext_dict)
        if index != None:
             ext_arr[i,index] = 1

        index = return_match_index(usr,i,usr_dict)
        if index != None:
             usr_arr[i,index] = 1

        #y_list.append(label)
        size_list.append(size)
        c1_list.append(c1)
        c2_list.append(c2)
        c3_list.append(c3)
        c4_list.append(c4)
        fi_list.append(uri)
        i+=1

    #"""
    #y_arr = np.array(y_list)
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

    return X,fi_list,size_list

def main():
    f = open('ext-dict-1236.json','r')
    ext_dict = json.load(f)
    f = open('usr-dict.json','r')
    usr_dict = json.load(f)
    X,files,size_list = create_input(ext_dict,usr_dict)
    np.savez('Input-test.npz',  data=X)
    start = time.time()
    DNN = TestModel.test_model(X,'model.h5')
    SVM = svm3.get_predictions(X,'libsvm.model')
    i = 0
    while(i < len(DNN) ):
       total = 0.53*float(DNN[i])+0.35*float(SVM[i][1])
       try:
          cur.execute('INSERT INTO score(uri,DNN,SVM,Size,UserRank,User,Total) VALUES(%s,%s,%s,%s,%s,%s,%s) on duplicate key update uri=%s,DNN=%s,SVM=%s,Size=%s,UserRank=%s,User=%s,Total=%s', (files[i],float(DNN[i]),float(SVM[i][1]),size_list[i]*normalize_size,0,"test-user",total,files[i],float(DNN[i]),float(SVM[i][1]),size_list[i]*normalize_size,0,'test-user',total))
          conn.commit()
       except:
          conn.rollback()
          raise
       i+=1
    
    hot_quota = 1200
    cur.execute('set @csum := 0')
    cur.execute('select uri from (select *,(@csum := @csum + Size) as cumulative_sum from score order by Total DESC ) as A where cumulative_sum > %s',[hot_quota])
    f = open('cold-files','w')
    results = cur.fetchall()
    for file in results:
        f.writelines(file['uri']+'\n')
    f.close()
    end = time.time()
    print("Elapsed time",end-start)
    #print(results)

#start process
if __name__ == '__main__':
    main()
