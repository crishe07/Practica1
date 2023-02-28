#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:14:09 2023

@author: alumno
"""

from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Manager
import random

K=10
NPROD = 3
N=5
 
def dar_numero(lvalue,semaf):
    if lvalue.value !=-1: #es trampa?
        semaf.acquire()
        if lvalue.value==-2:
            lvalue.value=random.randint(0,5) #inicilización
        else:
            lvalue.value+=random.randint(1,10)
        semaf.release()
            
        
def coger_numero(Lista,Lsemaf):
    m=100 #cota superior
    for i in range(NPROD):
        l=Lista[i].value
        if l < m and l!=-1: #es trampa?
            m=l
            k=i
    return (m,k) #devuelve tambien el productor que lo ha creado
    
        
def producer(lvalue, semaf, Empty, Nempty):
    for v in range(N+1):
        Empty.acquire() #espera a que consuma
        dar_numero(lvalue,semaf)
        
        print(f"producer {current_process().name} produciendo {lvalue.value} \n" )
        Nempty.release() #signal para que consuma
    
    lvalue.value=-1 #deja de producir 
        
    
    
def consumer(Lista, Lsemaf, Empty, Nempty, result):   
    for i in range(NPROD):
        Nempty[i].acquire() #espero a que produzcan
    
    for v in range(N*NPROD):
        (d,j)=coger_numero(Lista,Lsemaf)
        result.append((d,j)) 
        
        print(result)
        
        Empty[j].release() #signal para que produzca
        Nempty[j].acquire() #espero a que produzca
    
    return result
    
    
        

def main():
    values=[Value('i',-2) for i in range(NPROD)]
    Lsemaf=[Lock() for i in range(NPROD)]
    
    non_empty = [Semaphore(0) for i in range(NPROD)] 
    #non_empty ¿hay productos en producer?
    
    empty = [Lock() for i in range(NPROD)] 
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
    
    print (result)


if __name__ == '__main__':
    main()