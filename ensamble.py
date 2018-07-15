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
import create_input

size_num = 796847494129142/220*1e06 #Total size needed for storing all files
url = urlparse('mysql://user:pass@localhost:3306/test')

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
    return 0

def find_optimum():
	swap_auc = 0
	best_alpha,best_beta,best_gamma=0,0,0
	for alpha in [0.1*x for x in range(10)]:
		for beta in [0.1*y for y in range(10)]:
			for gamma in [0.1*z for z in range(10)]:
				auc=cal_auc(alpha,beta,gamma)				
				if swap_auc <= auc:
					swap_auc = auc
					best_alpha,best_beta,best_gamma=alpha,beta,gamma
				print(auc,alpha,beta,gamma)
	return best_alpha,best_beta,best_gamma,auc
					
				

def main():
    f = open('ext-dict-1236.json','r')
    ext_dict = json.load(f)
    f = open('usr-dict.json','r')
    usr_dict = json.load(f)
    usr_dict = {v:k for k,v in usr_dict.items()}
    X,files,size_list,usr_list,label_list = create_input.create_input("2015","10")
    DNN = TestModel.get_predictions(X,'DNN.h5')
    SVM = svm3.get_predictions(X,'libsvm.model')
    i = 0
    while(i < len(DNN) ):
       usr_rank = int(return_match_index(usr_list[i],0,usr_dict)) / 100
       total = float(DNN[i])+float(SVM[i][1])+float(usr_rank)
       try:
          cur.execute('INSERT INTO score(uri,DNN,SVM,Size,UserRank,User,Total,Label) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update uri=%s,DNN=%s,SVM=%s,Size=%s,UserRank=%s,User=%s,Total=%s', (files[i],float(DNN[i]),float(SVM[i][1]),size_list[i],usr_rank,usr_list[i],total,label_list[i],files[i],float(DNN[i]),float(SVM[i][1]),size_list[i],usr_rank,usr_list[i],total))
          conn.commit()
       except:
          conn.rollback()
          raise
       i+=1

def cal_qoe(hot_quota,alpha,beta,gamma):
	cur.execute('select count(*) act_hot from score where Label = 1')
	results = cur.fetchall()
	actual_hot = results[0]['act_hot']
	cur.execute('set @csum := 0')
	cur.execute('select count(*) pred_hot from (select *,(@csum := @csum + Size) as cumulative_sum from (select *,(%s*DNN+%s*SVM+%s*UserRank) Tscore from score) as B order by Tscore DESC) as A where cumulative_sum < %s) ',(alpha,beta,gamma,hot_quota))
	results = cur.fetchall()
	predicted_hot = results[0]['pred_hot']
	qoe = predicted_hot / actual_hot
	print(hot_quota,qoe)
	return qoe

def cal_auc(alpha,beta,gamma):
	hot_quota=[0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
	swap_quota=0
	swap_qoe=0
	qoe=0
	auc=0
	for quota in hot_quota:
		swap_qoe=cal_qoe(quota*size_num,alpha,beta,gamma)
		auc+=(qoe+swap_qoe)*(quota-swap_quota)*1/2
		qoe=swap_qoe
		swap_quota=quota
		print("qoe:{}".format(qoe))
	return auc

#start process
if __name__ == '__main__':
#    print(find_optimum())
    main()

