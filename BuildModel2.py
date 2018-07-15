import numpy as np
import keras
import h5py
from collections import Counter
import os
import time, sys, csv
from scipy import io
from sklearn.utils import shuffle
from scipy.sparse import csr_matrix, vstack,hstack, issparse
from keras.models import Sequential,load_model
from keras.layers import Dense, Dropout
from keras.callbacks import CSVLogger,EarlyStopping
import matplotlib.pyplot as plt
from keras import initializers,optimizers
from keras.utils import plot_model
import keras.backend as K

import tensorflow as tf
config=tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
K.set_session(sess)

def init(mean,stddev):
   return initializers.RandomNormal(mean=mean, stddev=stddev, seed=42)

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

def build_model(optimizer_name, activation,learning_rate,rho,epsilon,decay):
	print(activation,optimizer_name,learning_rate,rho,epsilon,decay)
	model = Sequential()
#	model.add(Dense(1500,init=init(0.0,0.05), input_dim=3209,activation=activation))
	model.add(Dense(1500,init=init(0.0,0.05), input_dim=2375,activation=activation))
	#model.add(Dense(128,init='normal', activation='relu'))
	model.add(Dense(500,init=init(0.0,0.05), activation=activation))
	model.add(Dense(70,init=init(0.0,0.05), activation=activation))
	#model.add(Dense(64,init='normal', activation='relu'))
	model.add(Dense(1, activation="sigmoid"))
#	model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
	if optimizer_name == 'rmsprop':	
		optimizer = optimizers.RMSprop(lr=learning_rate,rho=rho,epsilon=epsilon,decay=decay)
	if optimizer_name == 'Adam':
		print('not implemented')
	model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy',tp_score, tn_score,])	
	return model

def load_files(duration,temp):
	"""
	X_ = load_sparse_csr("random-data-"+duration+"day/ext-"+temp+".npz")
	Y_ = np.load("random-data-"+duration+"day/label-"+temp+".npy")
	S_ = np.load("random-data-"+duration+"day/size-"+temp+".npy")
	C1_= np.load("random-data-"+duration+"day/c1-"+temp+".npy")
	C2_= np.load("random-data-"+duration+"day/c2-"+temp+".npy")
	C3_= np.load("random-data-"+duration+"day/c3-"+temp+".npy")
	C4_= np.load("random-data-"+duration+"day/c4-"+temp+".npy")
	M = 200000
	X_ = X_[0:M].todense()
	Y_ = Y_[0:M]
	S_ = S_[0:M]
	C1_ = C1_[0:M]
	C2_ = C2_[0:M]
	C3_ = C3_[0:M]
	C4_ = C4_[0:M]
	Z = merge(X_,S_,C1_,C2_,C3_,C4_)
	print('dataset shape {}'.format(Counter(Y_)))
	return Z,Y_
	"""
	#"""
	X = np.load("ResampleData-"+temp+"day.npz")
	X = csr_matrix(X['data'])
	X = X.todense()
	Y = np.load("ResampleLabel-"+temp+"day.npy")
	print('Resampled dataset shape {}'.format(Counter(Y)))
	return X,Y
	#"""


def train_model(optimizer,activation,epoch,prev_epoch,Min,Max,duration,lr,rho,epsilon,decay):
	temp = "DB-"+str(Min)+"to"+str(Max)+'-'+str(duration)
	file_name = 'model-{}day-{}-{}-{}-{}-{}-{}-{}ep'.format(temp,activation,optimizer,str(lr),str(rho),str(epsilon),str(decay),str(prev_epoch))+'-non-weight.h5'
	if os.path.isfile(file_name) and epoch > prev_epoch :
		print('------------ find trained model ---------------------')
		model = load_model(file_name,custom_objects={'tp_score':tp_score, 'tn_score':tn_score})		
	else:
		model = build_model(activation,optimizer,lr,rho,epsilon,decay)
	X,Y = load_files(duration,temp)
	X,Y = shuffle(X,Y,random_state=42)

	print('Y {}'.format(Y))

	M = 900000

	slice = int(M*0.1)
	val_X = X[:slice]
	val_Y = Y[:slice]

	X = X[slice:M]
	Y = Y[slice:M]

	#class_weight={0:1,1:2}
	class_weight={0:1,1:1}
	temp2 = 'model-{}day-{}-{}-{}-{}-{}-{}-{}ep'.format(temp,activation,optimizer,str(lr),str(rho),str(epsilon),str(decay),str(epoch))
	out_filename = temp2+'-non-weight.h5'
	early_stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=2, mode='auto')
	csv_logger = CSVLogger('train-{}day-{}-{}-{}-{}-{}-{}-non-weight.csv'.format(temp,activation,optimizer,str(lr),str(rho),str(epsilon),str(decay)),separator=',',append=True)
	train_epoch = epoch -prev_epoch
	result = model.fit(X,Y,batch_size=64,epochs=train_epoch,verbose=2,validation_data=(val_X,val_Y),callbacks=[csv_logger],class_weight=class_weight,shuffle=True)
#initial_epoch=prev_epoch
	model.save(out_filename)

