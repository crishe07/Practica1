#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:14:09 2023

@author: alumno
"""

from multiprocessing import Process, current_process
from multiprocessing import Semaphore, Lock
from multiprocessing import Value, Manager
import random
import math


NPROD = 30 #numero de productores
N=15 #capacidad de los productores
 

def dar_numero(lvalue,semaf):
    assert lvalue.value != -1
    #if lvalue.value != -1: 
    semaf.acquire()
    if lvalue.value == -2:
        lvalue.value=random.randint(0,5) #inicilización
    else:
        lvalue.value+=random.randint(1,20) #creciente
    semaf.release()

        
def coger_numero(Lista,Lsemaf):
    m = math.inf
    for i in range(NPROD):
        l=Lista[i].value
        if l < m and l!=-1: 
            m=l
            k=i
    return (m,k) #devuelve tambien el productor que lo ha creado
    
        
def producer(lvalue, semaf, Empty, Nempty):
    for v in range(N):
        Empty.acquire() #espera a que consuma
        dar_numero(lvalue,semaf)
        
        print(f"producer {current_process().name} produciendo {lvalue.value} vuelta {v+1} \n" )
        Nempty.release() #signal para que consuma
    
    Empty.acquire() 
    
    lvalue.value=-1 #deja de producir 
    Nempty.release() 
    
    
def consumer(Lista, Lsemaf, Empty, Nempty, result):   
    for i in range(NPROD):
        Nempty[i].acquire() #espero a que produzcan
    
    while estan_produciendo(Lista):
        
        (d,j)=coger_numero(Lista,Lsemaf)
        
        result.append((d, f"prod {j}"))
        
        Empty[j].release() #signal para que produzca
        
        Nempty[j].acquire() #espero a que produzca
    
    return result
    

def estan_produciendo(Lista):
    b=False
    for i in Lista:
        if i.value!=-1:
            b=True
    return b
        

def main():
    values=[Value('i',-2) for i in range(NPROD)]
    Lsemaf=[Lock() for i in range(NPROD)]
   

    non_empty = [Semaphore(0) for i in range(NPROD)] #sem(0)
    #non_empty ¿hay productos en producer?
   
    empty = [Lock() for i in range(NPROD)] #sem(1)
    #empty: ¿esta vacio cada productor?
    
    
    manager=Manager()
    result=manager.list()
    
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
    
    print (result, len(result))


if __name__ == '__main__':
    main()