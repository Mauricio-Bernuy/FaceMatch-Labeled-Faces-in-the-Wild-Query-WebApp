import face_recognition
import pandas as pd
import numpy as np
import math
from pandas import DataFrame
import time


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ED = lambda X, Y : (sum((X - Y)**2))**0.5

K = 8 # K closest elements
N = 100 # N elements for collection

from rtree import index

p = index.Property()
p.dimension = 128 #D
p.buffering_capacity = 3 #M
p.dat_extension = 'data'
p.idx_extension = 'index'
idx = index.Index(properties=p)

import os
from face_recognition.face_recognition_cli import image_files_in_folder

my_dir = 'static/lfw/' # Folder where all your image files reside. Ensure it ends with '/
query_dl = 'static/query/'

encoding_for_file = [] # Create an empty list for saving encoded files
results_encodings = []
id_value=0

import shutil
for dir in [query_dl]:
    for path in os.listdir(dir):
        full_path = os.path.join(dir, path)
        shutil.rmtree(full_path, ignore_errors=True)

import threading
import itertools
from multiprocessing import Process, current_process, Queue 
import sys

Q = Queue()
def folder_process(i):
    added = False
    res=list()
    for j in os.listdir(my_dir+i):
        image = my_dir + i + '/' + j
        name = image
        image = face_recognition.load_image_file(image) # Run your load command
        image_encoding = face_recognition.face_encodings(image) # Run your encoding command
        if len(image_encoding) != 0:
            res.append((image_encoding[0], name)) # Append the results to encoding_for_file list
    return res
    
def assign_folders(folderlist,thread_num):
    print('thread',thread_num,'starting...')
    result = list()
    lng = len(folderlist)
    cnt = 0
    flag = False
    for i in folderlist:
        result = result + folder_process(i)

        cnt = cnt + 1
        per = (cnt/lng)*100
        if int(math.ceil(per)) % 5 == 0:
            if flag == False:
                print('thread',thread_num,':', per,'%','completed')
                flag = True
        else:
            flag = False
            
    print('thread',thread_num,'done!')
    Q.put(result)
    return

from heapq import heappush, heappop

def knn_search(image_encoding, k):
    global encoding_for_file
    priorityq = []
    distances = face_recognition.face_distance(results_encodings, image_encoding[0])
    for i in range(len(distances)):
        heappush(priorityq, (1/distances[i], encoding_for_file[i][1]))
        if(len(priorityq) > k): 
            heappop(priorityq)
    answers = sorted(priorityq, key=lambda tup: tup[0], reverse=True)
    return answers

def generate_encodings(N=-1):
    global encoding_for_file
    x=list()
    splitted = 0
    if N == -1:
        splitted = np.array_split(os.listdir(my_dir), 8)
    else:
        splitted = np.array_split(os.listdir(my_dir)[0:N], 8)

    worker_count = 8
    worker_pool = []
    for section in range(worker_count):
        p = Process(target=assign_folders, args=(splitted[section],section,))
        p.start()
        worker_pool.append(p)

    for p in range(worker_count):
        encoding_for_file = encoding_for_file + Q.get()

    cnt = 0
    for encoding in encoding_for_file:
        a=encoding[0]
        results_encodings.append(a)
        a = a.tolist() + a.tolist()
        idx.insert(cnt, a, obj=encoding[1])
        cnt = cnt + 1

indexstore_dir = 'indexstore/'
import pickle

def clear_files():
    idx = 0
    idx = index.Index(properties=p)
    encoding_for_file = []
    results_encodings = []
    
def write_encodings(N=-1):
    global encoding_for_file
    if N == -1:
        pickle.dump(encoding_for_file, open( indexstore_dir + 'indexdata_' + "COMPLETE" + '.dat', "wb" ))
    else:
        pickle.dump(encoding_for_file, open( indexstore_dir + 'indexdata_' + str(N) + 'N.dat', "wb" ))

def load_encodings(N=-1):
    global encoding_for_file
    if N == -1:
        encoding_for_file = list(pickle.load(open(indexstore_dir + 'indexdata_' + "COMPLETE" + '.dat', "rb" )))
    else:
        encoding_for_file = list(pickle.load(open(indexstore_dir + 'indexdata_' + str(N) + 'N.dat', "rb" )))

    cnt = 0
    for encoding in encoding_for_file:
        a=encoding[0]
        results_encodings.append(a)
        a = a.tolist() + a.tolist()
        idx.insert(cnt, a, obj=encoding[1])
        cnt = cnt + 1

def image_search(name_input, K, rtree_seq):
    name_input = "site:wikipedia.org " + name_input

    import modified_bing_downloader as downloader
    downloader.download(name_input, limit=1,  output_dir=query_dl, 
    adult_filter_off=True, force_replace=False, timeout=60)

    ss = os.listdir(query_dl+name_input)[0]
    ss = query_dl + name_input + '/' + ss

    return analyze_and_return(ss, K, rtree_seq)

def analyze_and_return(img_directory, K, rtree_seq):
    image_encoding = face_recognition.face_encodings(face_recognition.load_image_file(img_directory))

    if len(image_encoding) == 0:
        print('No se encontró una cara en tu búsqueda, ¿podría ser más específico?')
        return tuple()
    else:
        q = image_encoding[0].tolist()
        
        if rtree_seq == "rtree":
            rtree_start = time.time()
            hits=idx.nearest(q, objects=True, num_results=K)
            rtree_end = time.time()

            print("\nLos",K,"vecinos mas cercanos de",img_directory,"usando r-tree son: ")
            r = list()
            for n in hits:
                a = n.object
                r.append(a)
                print(a)
            print("r-tree took ", rtree_end - rtree_start)
            return (img_directory, r, rtree_end - rtree_start)
            
        if rtree_seq == "seq":
            knn_start = time.time()
            knn_results = knn_search(image_encoding, K)
            knn_end = time.time()
            print("\nLos",K,"vecinos mas cercanos de",img_directory,"usando knn secuencial son: ", knn_results)
            print("knn took ", knn_end - knn_start)
            return (img_directory, [n[1] for n in knn_results], knn_end - knn_start)


# load_encodings(10)
# print(image_search("Danny Trejo", 8, "rtree"))
# print(analyze_and_return("lfw/Abbas_Kiarostami/Abbas_Kiarostami_0001.jpg",8,"seq"))


# while 1:
#     print("\n\nWho you wanna search?:")
#     name_input = input()
#     name_input = "site:wikipedia.org " + name_input
#     import modified_bing_downloader as downloader

#     downloader.download(name_input, limit=1,  output_dir=query_dl, 
#     adult_filter_off=True, force_replace=False, timeout=60)
#     ss = os.listdir(query_dl+name_input)[0]
#     ss = query_dl + name_input + '/' + ss

#     image_encoding = face_recognition.face_encodings(face_recognition.load_image_file(ss))

#     print("\nImagen de entrada:")
#     print(ss)
#     if len(image_encoding) == 0:
#         print('No se encontró una cara en tu búsqueda, ¿podría ser más específico?')
#     else:
#         q = image_encoding[0].tolist()
#         rtree_start = time.time()
#         hits=idx.nearest(q, objects=True, num_results=K)
#         rtree_end = time.time()

#         print("\nLos",K,"vecinos mas cercanos de",name_input,"son: ")
#         print("r-tree took ", rtree_end - rtree_start)
#         for n in hits:
#             a = n.object
#             print(a)
#         knn_start = time.time()
#         knn_results = knn_search(image_encoding, K)
#         knn_end = time.time()
#         print("\nLos",K,"vecinos mas cercanos de",name_input," usando knn son: ", knn_results)
#         print("knn took ", knn_end - knn_start)