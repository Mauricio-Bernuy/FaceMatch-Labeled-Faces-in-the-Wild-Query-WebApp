from multiprocessing import Process, current_process, Manager, Queue
import sys

result = list()
Q = Queue()


def add():
    res = list()
    for i in range(10):
        res.append(i)  
    Q.put(res)


worker_count = 8
worker_pool = []
for section in range(worker_count):
    p = Process(target=add)
    p.start()
    result = result + Q.get()
    worker_pool.append(p)
for p in worker_pool:
    a = p.join()

print(result)