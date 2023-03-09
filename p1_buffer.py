#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:14:09 2023

@author: alumno
"""

from multiprocessing import Process, current_process
from multiprocessing import Semaphore, Lock
from multiprocessing import Value, Manager, Array
import random
import math


NPROD = 3 #numero de productores
LPROD= 5 #capacidad del array de los productores
N=15 #capacidad de los productores
 

def dar_numero(array,semaf):
    assert array[0]!=-1
    semaf.acquire()
    if array[0] == -2:
        array[0]=random.randint(0,5) #inicilización
        print("inicio", array[0])
    else:
        for i in range(1,len(array)):
            if array[i]==-2:
                array[i]=array[i-1] +random.randint(1,20) #creciente
                print("produciendo", array[i])
                break
    semaf.release()

        
def coger_numero(ListaA,Lsemaf):
    m = math.inf
    for i in range(NPROD):
        l=ListaA[i][0]
        if l < m and l!=-1: 
            m=l
            k=i
         #avanzamos ListaA[k]
        for j in range(LPROD-1):
            ListaA[k][j]=ListaA[k][j+1]
        ListaA[k][LPROD-1]=-2
    return (m,k) #devuelve tambien el productor que lo ha creado
    
        
def producer(lvalue, semaf, Empty, Nempty):
    for v in range(N):
        Empty.acquire() #espera a que consuma
        dar_numero(lvalue,semaf)
        
        print(f"producer {current_process().name} produciendo {lvalue[0]} vuelta {v+1} \n" )
        Nempty.release() #signal para que consuma
    
    Empty.acquire() 
    
    lvalue[0]=-1 #deja de producir 
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
        if i[0]!=-1:
            b=True
    return b
        

def main():
    #values=[Value('i',-2) for i in range(LPROD)]
    
    Lsemaf=[Lock() for i in range(NPROD)]
   

    non_empty = [Semaphore(0) for i in range(NPROD)] #sem(0)
    #non_empty ¿hay productos en producer?
   
    empty = [Lock() for i in range(NPROD)] #sem(1)
    #empty: ¿esta vacio cada productor?
    
    almacen=Array('i',LPROD)
    for i in range(LPROD):
        almacen[i]=-2
    
    Alm=[almacen for i in range(NPROD)]
    
    #Añadir lista de indices
    
    
    
    manager=Manager()
    result=manager.list()
    
    prodlst = [Process(target=producer,
                        name=f'prod_{i}',
                        args=(Alm[i], Lsemaf[i], empty[i], non_empty[i]))
                for i in range(NPROD) ]

    consum= Process(target=consumer,
                    name= "consumidor", 
                    args=(Alm, Lsemaf, empty, non_empty, result))
    
    
    for p in prodlst:
        p.start()
    consum.start()
        
    for p in prodlst:
        p.join()
    consum.join()
       
    print (result, len(result))


if __name__ == '__main__':
    main()