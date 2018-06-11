import sklearn
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import json
import keras
import h5py
from collections import Counter
from keras.callbacks import ModelCheckpoint
import time, sys, csv
from scipy import io
from scipy.sparse import csr_matrix, vstack,hstack, issparse
from keras.models import Sequential,load_model
from keras.layers import Dense, Dropout
import keras.backend as K

def tp_score(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def tn_score(y_true, y_pred):
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos
    y_pos = K.round(K.clip(y_true, 0, 1))
    y_neg = 1 - y_pos
    tn = K.sum(y_neg * y_pred_neg) / K.sum(y_neg + K.epsilon())
    return tn


def get_file_size(X):
#	print(X)
	size = round(X*17940408164) # get file size (MB)
	size = size /1000/1000
	return size

def return_extension_name(X):
	f = open('ext-dict-1236.json','r')
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
	f = open('usr-dict.json','r')
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

def load_sparse_csr(filename):
	loader = np.load(filename)
	return csr_matrix((loader['data'], loader['indices'], loader['indptr']),shape=loader['shape'])

def merge(X,S,C1,C2,C3,C4):
	Z = np.c_[X,S]
	Z = np.c_[Z,C1]
	Z = np.c_[Z,C2]
	Z = np.c_[Z,C3]
	Z = np.c_[Z,C4]
	return Z

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
	list.append(predict[0][0])
	list.append(true[0])
	list.append(proba)
	return list

def test_model(input,file_name):
	return get_confusion_matrix(input,file_name)
#	get_csv_predict(optimizer,activation,epoch,Min,Max,duration,span,lr,rho,epsilon,decay)

def get_confusion_matrix(input,file_name):
	model = load_model(file_name,custom_objects={'tp_score':tp_score, 'tn_score':tn_score})
	X_ = input
	X_=X_[0:600000]
	start = time.time()
	#predictions = model.predict_classes(X_,batch_size=64, verbose=0)
	predictions = model.predict(X_,batch_size=64, verbose=0)
	end = time.time()-start
#	print('time : {}'.format(end))
#	print('DNN result',predictions)
	return predictions

def get_csv_predict(file_name):
#	temp = "DB-"+str(Min)+"to"+str(Max)+'-'+str(duration)
	temp = "DB-0to30-30"
	file = 'model-{}day-{}-{}-{}-{}-{}-{}'.format(temp,activation,optimizer,str(lr),str(rho),str(epsilon),str(decay))+"-non-weight-0213.h5"

	model = load_model(file,custom_objects={'tp_score':tp_score, 'tn_score':tn_score})

	temp = "DB-"+str(Min+span)+"to"+str(Max+span)+'-'+str(duration)
	X_name = "ResampleData-"+temp+"day.npz"
	Y_name = "ResampleLabel-"+temp+"day.npy"
	f_name = "file-"+temp+"day.npy"

	f = open('predict-result-{}-day-{}-{}-{}-{}-{}-{}.csv'.format(temp,activation,optimizer,str(lr),str(rho),str(epsilon),str(decay)),'w')
	csv_writer = csv.writer(f)
	csv_writer.writerow(['file','extension','size(MB)','usr','1st','2nd','3rd','4th','predict_class','true_class','proba'])

	print('test data is {}'.format(X_name))
	X_ = np.load(X_name)
	X_ = csr_matrix(X_['data']).todense()
	Y_ = np.load(Y_name)
#	f_ = np.load(f_name)[0:600000]
	f_ = np.load(f_name)

	for i in range(0,X_.shape[0]):
		X_test = X_[i]
		ext = return_extension_name(X_[i,:1236].getA()[0])
		usr = return_usr_name(X_[i,1236:-6].getA()[0])
		size = get_file_size(X_[i,-5])
		first,second,third,forth = get_access_pattern(X_[i,-4],X_[i,-3],X_[i,-2],X_[i,-1])
		Y_test = Y_[i]
		file = f_[i]
		Y_test = np.array([Y_test])
		predict_class = model.predict_classes(X_test,verbose=2)
		proba = model.predict(X_test,batch_size=64,verbose=2)
		proba = float(proba[0][0])
		csv_writer.writerow(make_output_list(file,ext,size,usr,first,second,third,forth,predict_class,Y_test,proba))
