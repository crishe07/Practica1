#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:14:09 2023

@author: alumno
"""

from multiprocessing import Process, current_process
from multiprocessing import Semaphore, Lock, BoundedSemaphore
from multiprocessing import Value, Manager, Array
import random
import math


NPROD = 3 #numero de productores
LPROD= 5 #capacidad del array de los productores
N=8#capacidad de los productores
 

def dar_numero(array, index, semaf):
    semaf.acquire()
    try:
        if index.value==0: #inicilización
            array[index.value]=random.randint(0,5) 
        else:
            array[index.value]=array[index.value-1] +random.randint(1,10) #creciente
        print(f"generado {array[index.value]} desde productor {current_process().name} \n")
        index.value+=1
    finally:
        semaf.release()
        

def avanzar(array,index, semaf):
    semaf.acquire()
    try:
        for i in range(len(array)-1):
            if array[i] !=-2:
                array[i]=array[i+1]
    
        array[-1]=-2
        index.value-=1
    finally:
        semaf.release()
        
def coger_numero(ListaA,indexs, Lsemaf):
    m = math.inf
    for i in range(NPROD):
        l=ListaA[i][0]
        if l < m and l!=-1: 
            m=l
            k=i
    
    print(f"avanzando array {k} \n")
    
    avanzar(ListaA[k],indexs[k],Lsemaf[k])
    
    return (m,k) #devuelve tambien el productor que lo ha creado
    

        
def producer(aray, index, semaf, Empty, Nempty):
    for v in range(N):
        Empty.acquire() #espera a que consuma 
        
        dar_numero(aray,index,semaf)
                
        Nempty.release() #signal para que consuma
        
    
    Empty.acquire() 
    aray[index.value]=-1 #deja de producir 
    Nempty.release() 
    
    
def consumer(ListaA, index, Lsemaf, Empty, Nempty, result):   
    for i in range(NPROD):
        
        Nempty[i].acquire() #espero a que produzcan
    
    while estan_produciendo(ListaA):
        
        (d,j)=coger_numero(ListaA, index, Lsemaf)
        
        
        result.append((d, f"prod {j}"))
        
        
        Empty[j].release() #signal para que produzca
        
        Nempty[j].acquire() #espero a que produzca
    
    return result
    

def estan_produciendo(ListaA): 
    b=False
    for alm in ListaA:
        if alm[0]!=-1:
            b=True
    return b
        

def main():
    
    Lsemaf=[Lock() for i in range(NPROD)] #semaforo individual de cada productor

    non_empty = [Semaphore(0) for i in range(NPROD)]  #non_empty ¿hay productos en producer?
   
    empty = [BoundedSemaphore(LPROD) for i in range(NPROD)]  #empty: ¿esta vacio cada productor?
    
       
    Alm=[Array('i',LPROD) for i in range(NPROD)] #un array para cada productor
    for almacen in Alm:
        for i in range(LPROD):
            almacen[i]=-2
    
    indices=[Value('i',0) for i in range(NPROD)] #indice que indica la ultima posicion del buffer donde hay un elemento
    
    manager=Manager()
    result=manager.list() #lista resultado, donde el consumidor va poniendo los elementos ordenados
    
    prodlst = [Process(target=producer,
                        name=f'prod_{i}',
                        args=(Alm[i], indices[i], Lsemaf[i], empty[i], non_empty[i]))
                for i in range(NPROD) ]

    consum= Process(target=consumer,
                    name= "consumidor", 
                    args=(Alm, indices, Lsemaf, empty, non_empty, result))
    
    
    for p in prodlst:
        p.start()
    consum.start()
        
    for p in prodlst:
        p.join()
    consum.join()
       
    print (result, len(result))


if __name__ == '__main__':
    main()