#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:14:09 2023

@author: alumno
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value
import random

K=10
NPROD = 3
N=2
 
def dar_numero(lvalue,semaf):
    if lvalue.value !=-1:
        semaf.acquire()
        n=random.randint(1,10)
        lvalue.value=n
        semaf.release()
            
        
def coger_numero(Lista,Lsemaf):
    m=11
    for i in range(NPROD):
        l=Lista[i].value
        if l < m and l!=-1:
            m=l
            k=i
        else:
            print("fallo")
            #k=-1
    return (m,k)
    
        
def producer(lvalue, semaf, Empty, Nempty):
    for v in range(N):
        Empty.acquire() #espera a que consuma
        dar_numero(lvalue,semaf)
        print(f"producer {current_process().name} produciendo {lvalue.value} \n" )
        Nempty.release() #signal para que consuma
    #Empty.acquire()
    #lvalue.value=-1 #deja de producir 
        
    
    
def consumer(Lista, Lsemaf, Empty, Nempty, result):   
    for i in range(NPROD):
        Nempty[i].acquire() #espero a que produzcan
    for v in range(N*NPROD):
        (d,j)=coger_numero(Lista,Lsemaf)
        result.append(d)
        print(result)
        Empty[j].release() #signal para que produzca
        Nempty[j].acquire() #espero a que produzca
    #return result
    
    
        

def main():
    values=[Value('i',-2) for i in range(NPROD)]
    Lsemaf=[Lock() for i in range(NPROD)]
   
    
    result=[]

    non_empty = [Semaphore(0) for i in range(NPROD)] #sem(0)
    #non_empty ¿hay productos en producer?
    empty = [Lock() for i in range(NPROD)] #sem(1)
    #empty: ¿esta vacio cada productor?
    
    
    prodlst = [Process(target=producer,
                        name=f'prod_{i}',
                        args=(values[i], Lsemaf[i], empty[i], non_empty[i]))
                for i in range(NPROD) ]

    consum= Process(target=consumer,
                    name= "consumidor", 
                    args=(values, Lsemaf, empty, non_empty, result))
    
    for p in prodlst:
        p.start()
    consum.start()
    
    for p in prodlst:
        p.join()
    consum.join()
    
    print (result)


if __name__ == '__main__':
    main()