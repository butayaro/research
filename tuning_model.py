import BuildModel2
lr = 0.001
rho = 0.9
epsilon = 1e-08
decay = 0.0
optimizer = 'rmsprop'
activation = 'sigmoid'
duration = 30

#for lr in [1e-05,1e-04,1e-03,0.01,0.1]:
for lr in [1e-04]:
	prev_epoch=500
	for epoc in [1000,1500,2000]:
		BuildModel2.train_model(activation,optimizer,epoc,prev_epoch,0,90,duration,lr,rho,epsilon,decay)
		prev_epoch = epoc

lr = 0.001
rho = 0.9
epsilon = 1e-08
decay = 0.0

for rho in [0.009,0.09,0.99,0.999]:
	prev_epoch=0
	for epoc in [500]:
		BuildModel2.train_model(activation,optimizer,epoc,prev_epoch,0,90,duration,lr,rho,epsilon,decay)
		prev_epoch = epoc
	
lr = 0.001
rho = 0.9
epsilon = 1e-08
decay = 0.0
for epsilon in [1e-04,1e-12]:
	prev_epoch=0
	for epoc in [500]:
		BuildModel2.train_model(activation,optimizer,epoc,prev_epoch,0,90,duration,lr,rho,epsilon,decay)
		prev_epoch = epoc

