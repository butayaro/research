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

def create_input(year,month):
    i = 0
    row = 137765
    ext_arr = lil_matrix((row,1236))
    usr_arr = lil_matrix((row,100))
    size_list,c1_list,c2_list,c3_list,c4_list,fi_list,y_list=[],[],[],[],[],[],[]

    #X = ext_arr
    X = ext_arr.tocsr().todense()
    usr = usr_arr.tocsr().todense()

def main():
    create_input("2015","09")
    # DNN = TestModel.test_model(X,'model.h5')
    # SVM = svm2.testing(X,'libsvm.model')
    # i = 0
    # while(i < len(DNN) ):
    #    total = float(DNN[i])+float(SVM[i][1])
    #    try:
    #       cur.execute('INSERT INTO score(uri,DNN,SVM,Size,UserRank,User,Total) VALUES(%s,%s,%s,%s,%s,%s,%s) on duplicate key update uri=%s,DNN=%s,SVM=%s,Size=%s,UserRank=%s,User=%s,Total=%s', (files[i],float(DNN[i]),float(SVM[i][1]),size_list[i],0,"test-user",total,files[i],float(DNN[i]),float(SVM[i][1]),size_list[i],0,'test-user',total))
    #       conn.commi616t()
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
