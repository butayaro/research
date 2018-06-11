import numpy as np
import sklearn
import sys
from svm import *
from svmutil import *
from sklearn.metrics import confusion_matrix
from sklearn.utils import shuffle
from scipy.sparse import csr_matrix, vstack,hstack, issparse
from collections import Counter
sys.path.append('/home/r_irie/jstest/libsvm-3.22/tools')
#from grid import *
import time,csv,json

def get_file_size(X):
#	print(X)
	size = round(X*17940408164) # get file size (MB)
	size = size /1000/1000
	return size

def return_extension_name(X):
	f = open('/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/ext-dict-1236.json','r')
	ext_dict = json.load(f)

	i = 0
	index = -1
	for element in X:
		if element == 1:
			index = i
			break
		i+=1

	if not index == -1:
		for k in ext_dict:
			if ext_dict[k] == index:
				extension = k
				break
	else:
		extension = 'other'
	return extension

def return_usr_name(X):
	f = open('/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/usr-dict.json','r')
	usr_dict = json.load(f)

	i = 0
	index = -1
	for element in X:
		if element == 1:
			index = i
			break
		i+=1

	if not index == -1:
		for k in usr_dict:
			if usr_dict[k] == index:
				usr = k
				break
	else:
		usr = 'other'
	return usr

def get_access_pattern(first,second,third,forth):
	first = round(first * 30)
	second = round(second * 19)
	third = round(third * 20)
	forth = round(forth * 17)
	return first,second,third,forth

def load_files(duration,temp):
	X = np.load("/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/ResampleData-"+temp+"day.npz")
	X = csr_matrix(X['data'])
	X = X.todense()
	Y = np.load("/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/ResampleLabel-"+temp+"day.npy")
	print('Resampled dataset shape {}'.format(Counter(Y)))
	return X,Y

def training(Min,Max,duration):
	temp = "DB-"+str(Min)+"to"+str(Max)+'-'+str(duration)
	X,Y = load_files(duration,temp)

	X,Y = shuffle(X,Y,random_state=42)

	M = 300000
	X = X[0:M]
	Y = Y[0:M]

	slice = int(M*0.1)
	val_X = X[:slice]
	val_Y = Y[:slice]

	X = X[slice:M].tolist()
	Y = Y[slice:M].tolist()
	print('Y {}'.format(Counter(Y)))

	prob=svm_problem(Y,X)
	print('test using gpu prepare')
	param=svm_parameter('-t 0 -c 1 -b 1')
	start = time.time()
	print('test using gpu start')
	m = svm_train(prob, param)
	end = time.time()-start
	svm_save_model('libsvm.model', m)
	print("processing time {}".format(end))

def make_output_list(file,ext,size,usr,first,second,third,forth,predict,true,proba):
	list=[]
	list.append(file)
	list.append(ext)
	list.append(size)
	list.append(usr)
	list.append(first)
	list.append(second)
	list.append(third)
	list.append(forth)
	list.append(predict[0])
	list.append(true[0])
	list.append(proba)
	return list

def get_csv_predict(Min,Max,duration):
	temp = "DB-"+str(Min)+"to"+str(Max)+'-'+str(duration)
	m = svm_load_model('libsvm.model')
	temp = "DB-"+str(Min)+"to"+str(Max)+'-'+str(duration)
	X_name = "/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/ResampleData-"+temp+"day.npz"
	Y_name = "/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/ResampleLabel-"+temp+"day.npy"
#	f_name = "file-DB-{}to{}.npy".format(Min,Max)
	f_name = "/home/r-irie/Lab/data/training_data/workspace/workspace_until0109/until1229/1236-ext/file-"+temp+"day.npy"

	f = open('svm.csv','w')
	csv_writer = csv.writer(f)
	csv_writer.writerow(['file','extension','size(MB)','usr','1st','2nd','3rd','4th','predict_class','true_class','proba'])

	print('test data is {}'.format(X_name))
	X_ = np.load(X_name)
	X_ = csr_matrix(X_['data']).todense().tolist()
	Y_ = np.load(Y_name).tolist()
#	f_ = np.load(f_name)[0:600000]
	f_ = np.load(f_name)
	Y_test=[]
#	print("X:{}".format(X_))
	print("Y:{}".format(len(Y_)))

	for i in range(len(X_)):
		X_test = X_[i]
		ext = return_extension_name(X_[i][:1236])
		usr = return_usr_name(X_[i][1236:-6])
		size = get_file_size(X_[i][-5])
		first,second,third,forth = get_access_pattern(X_[i][-4],X_[i][-3],X_[i][-2],X_[i][-1])
		Y_test = [Y_[i]]
		file = f_[i]
		#print("i:{},X:{}".format(i,len(X_test)))
		#print("x:{}".format(X_[i]))
		#print("Y:{}".format(Y_test))

		p_labels, p_acc, p_vals = svm_predict(Y_test, [X_test], m,'-b 1')
		proba = float(p_vals[0][1])
		print(proba)
		predict_class = p_labels
#		print("1:{},2:{},3:{},4:{},pre:{},tru:{},pro:{}".format(first,second,third,forth,predict_class,Y_test,proba))
#		if proba < 0.5:
#			proba = 1 - proba
		csv_writer.writerow(make_output_list(file,ext,size,usr,first,second,third,forth,predict_class,Y_test,proba))

def testing(X,model_name):
	#X = csr_matrix(X_['data']).todense().tolist()
	X = X.tolist()
	Y = [0 for i in range(len(X))]
	m = svm_load_model(model_name)
	start = time.time()
	p_labels, p_acc, p_vals = svm_predict(Y, X, m,'-b 1')
	end = time.time()-start
	#print('SVM results:',p_labels) #予測結果
	return p_vals

def tuning(Min,Max,duration):
	#"""
	temp = "DB-"+str(Min)+"to"+str(Max)+'-'+str(duration)
	X,Y = load_files(duration,temp)

	X,Y = shuffle(X,Y,random_state=42)

	M = 300000
	X = X[0:M]
	Y = Y[0:M]

	slice = int(M*0.1)
	val_X = X[:slice]
	val_Y = Y[:slice]

	X = X[slice:M]
	Y = Y[slice:M].T
	X = np.c_[Y,X].tolist()

	f = open('dataset2.txt', 'w')
	for x in X:
		k=0
		for y in x:
			if k != 0:
				f.write(str(k)+":"+str(y)+" ")
			else:
				f.write(str(y)+" ")
			k+=1
		f.write("\n")
	f.close()
	#"""
#	rate,params=find_parameters('dataset.scale')
#	print("rate:{},params:{}".fomart(rate,params))

#training(0,30,30)
#testing(0,30,30)
#get_csv_predict(0,60,30)
#testing(0,60,30)
#tuning(0,60,30)
