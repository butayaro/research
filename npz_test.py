#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import codecs
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
import sys
import collections

def get_extension_group(extension):
	audio=['.aif','.cda','.mid','.mp3','.midi','.mpa','.ogg','.wav','.wma','.wpl']
	compressed=['.7z','.arj','.deb','.pkg','.rar','.rpm','.gz','.z','.zip','.cab','.dmg','.lz']
	disc=['.bin','.dmg','.iso','.toast','.vcd','.img']
	data=['.csv','.dat','.db','.dbf','.log','.mdb','.sav','.sql','.tar','.xml','.xls','.xlsx','.xlr','.ods']
	executable=['.apk','.bat','.bin','cgi.','.pl','.com','.exe','.gadget','.jar','.py','.wsf','.dcu']
	font=['.fnt','.fon','.otf','.ttf']
	image=['.ai','.bmp','.gif','.ico','.jpeg','.jpg','.png','.ps','.psd','.svg','.tif','.tiff']
	internet=['.asp','.aspx','.cer','.cfm','.css','.htm','.html','.js','.jsp','.part','.php','.rss','.xhtml']
	presentation=['.key','.odp','.pps','.ppt','.pptx','.pot']
	program=['.c','.class','.cpp','.cs','.h','.java','.sh','.swift','.vb','.m','.pas','.hpp']
	system=['.bak','.cab','.cfg','.cpl','.cur','.dll','.dmp','.drv','.icns','.ico','.ini','.lnk','.msi','.sys','.tmp']
	video=['.3gs','.3gp','.avi','.flv','.h264','.m4v','.mkv','.mov','.mp4','.mpg','.mpeg','.rm','.swf','.vob','.wmv']
	word=['.doc','.docx','.odt','.pdf','.rtf','.tex','.txt','.wks','.wps','.wpd']

	if extension in audio:
		 return 'audio'
	if extension in compressed:
		 return 'compressed'
	if extension in disc:
		 return 'disc'
	if extension in data:
		 return 'data'
	if extension in executable:
		 return 'executable'
	if extension in font:
		 return 'font'
	if extension in image:
		 return 'image'
	if extension in internet:
		 return 'internet'
	if extension in presentation:
		 return 'presentation'
	if extension in program:
		 return 'program'
	if extension in system:
		 return 'system'
	if extension in video:
		 return 'video'
	if extension in word:
		 return 'word'
	else:
		return extension

def input():
    args = sys.argv
    argv = len(args)
    if argv == 4:
       Min = int(args[1])
       Max = int(args[2])
       duration = int(args[3])
    else:
       print("please input min day ")
       Min = int(input())
       print("please input duration of prediction ")
       duration = int(input())
       Max = Min + duratio
    return Min,Max,duration

if __name__ == "__main__":
    Min,Max,duration = input()

    f = open('ext-dict-1236.json','r')
    ext_dict = json.load(f)
    f = open('usr-dict.json','r')
    usr_dict = json.load(f)


    i = 0
    row = 100
    max = len(ext_dict)
    ext_shape = [row,max]
    ext_arr = lil_matrix((row,max))
    max = len(usr_dict)
    usr_shape = [row,max]
    usr_arr = lil_matrix((row,max))
    y_list = []
    size_list = []
    c1_list = []
    c2_list = []
    c3_list = []
    c4_list = []
    fi_list = []

    print("row:{},ext:{},usr{}".format(row,len(ext_dict),len(usr_dict)))
    for temp in db.find({},no_cursor_timeout=True):
        size = temp['size'] / 17940408164 # nomarlize
        ext = temp['extention'].lower()
        ext = get_extension_group(ext)
        usr = temp['5'].lower()
        label_name = 'label-'+str(duration)+'day'
        label = temp[label_name]
        file = temp['file']
        for element in ext_dict:
            if ext == element:
                 index = ext_dict[ext]
                 ext_arr[i,index] = 1
                 break


        for element in usr_dict:
            if usr == element:
                 index = usr_dict[usr]
                 usr_arr[i,index] = 1
                 break
#        print('i:{},index:{}'.format(i,index))


        y_list.append(label)
        size_list.append(size)

        c1_list.append(temp['1st']/20)
        c2_list.append(temp['2nd']/20)
        c3_list.append(temp['3rd']/20)
        c4_list.append(temp['4th']/20)
        fi_list.append(file)
        i+=1

#    print('c1-arr:{}'.format(collections.Counter(c1_list)))
#    print('c2-arr:{}'.format(collections.Counter(c2_list)))

    y_arr = np.array(y_list)
    s_arr = np.array(size_list)
    c1_arr = np.array(c1_list)
    c2_arr = np.array(c2_list)
    c3_arr = np.array(c3_list)
    c4_arr = np.array(c4_list)
    fi_arr = np.array(fi_list)

    b = ext_arr.tocsr()
    data = b.data
    indices = b.indices
    indptr = b.indptr
    np.savez('ext-'+target+'.npz', shape=ext_shape, data=data,indices=indices,indptr=indptr)

    b = usr_arr.tocsr()
    data = b.data
    indices = b.indices
    indptr = b.indptr
    np.savez('usr-'+target+'.npz', shape=usr_shape, data=data,indices=indices,indptr=indptr)

    np.save('label-'+target+'.npy',y_arr)
    np.save('size-'+target+'.npy',s_arr)
    np.save('c1-'+target+'.npy',c1_arr)
    np.save('c2-'+target+'.npy',c2_arr)
    np.save('c3-'+target+'.npy',c3_arr)
    np.save('c4-'+target+'.npy',c4_arr)
    np.save('file-'+target+'.npy',fi_arr)
