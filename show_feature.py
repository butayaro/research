import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt

plt.style.use('ggplot')
#font = {'family' : 'meiryo'}
#matplotlib.rc('font', **font)
#mpl.rcParams['agg.path.chunksize'] = 100000000

def plot_hist(var1,df):
	df = df.sort_values(by="count",ascending=True)
	df = df.reset_index(drop=True)
	ax = df.plot(y='count',bins=500,logy=True,kind="hist",legend=True)
	ax.set_xlabel('{}'.format(var1))
	ax.set_ylabel('# of access')
	ax.set_title("Histgram Access-{}".format(var1))
	plt.savefig(var1+'hist')
	
def plot_line(var1,df):
	df = df.sort_values(by="count",ascending=True)
	df = df.reset_index(drop=True)
	#print(len(df.index))
	#index = pd.DataFrame(range(len(df.index)),columns='index')
	#df = pd.concat([df,index],axis=1)
	#df = df["count"]
	#print(df)
	#df.plot.scatter(x="vid",y="count")

	ax = df.plot(y="count",logx=True,logy=True,legend=True,kind="line")
	#ax = df.plot(y='count',bins=500,logy=True,kind="hist",legend=True,ylim=[0,10000])
	#plt.semilogy(x,y)
	ax.set_xlabel('Cumulative # of {}'.format(var1))
	ax.set_ylabel('# of access')
	ax.set_title("Access-Cumulative # of {}".format(var1))
	#plt.show()

	plt.savefig(var1+'lines')

def plot_line2(var1,df,x="vid",y="count"):
	df = df.sort_values(by=x,ascending=True)
	df = df.reset_index(drop=True)
	#print(len(df.index))
	#index = pd.DataFrame(range(len(df.index)),columns='index')
	#df = pd.concat([df,index],axis=1)
	#df = df["count"]
	#print(df)
	#df.plot.scatter(x="vid",y="count")

	ax = df.plot(x=x,y=y,logx=True,logy=True,legend=True,kind="scatter")
	#ax = df.plot(y='count',bins=500,logy=True,kind="hist",legend=True,ylim=[0,10000])
	#plt.semilogy(x,y)
	ax.set_xlabel("Size of Video(Bytes)")
	ax.set_ylabel('# of access')
	ax.set_title("Access-Cumulative # of {}".format(var1))
	#plt.show()

	plt.savefig(var1+'lines')

def replace_outlier(df, bias=1.5):
    #四分位数
    series = df['vid']
    q1 = series.quantile(.25)
    q3 = series.quantile(.75)
    iqr = q3 - q1

    #外れ値の基準点
    outlier_min = q1 - (iqr) * bias
    outlier_max = q3 + (iqr) * bias

    print("outlier_min :" + str(outlier_min) + ", outlier_max :" + str(outlier_max))

    #外れ値をクリップする
    #df = df.clip(outlier_min, outlier_max)
    df.drop(df.index[df['vid'] > outlier_max],inplace=True)
    print(df.corr())
    return series

if __name__ == '__main__': 
	var1='Size(bytes)'
	df = pd.read_csv('size-access.csv',names=["count","vid"])
#	df = pd.read_csv('vid-access.csv',names=["vid","count"])
#	df.drop(df.index[df['vid'] == 0],inplace=True)
	print(df)
	replace_outlier(df,1.5)
	print(df.corr())
#	plot_hist(var1,df)
	plot_line2(var1,df,"count","vid")
#	plot_line(var1,df)
