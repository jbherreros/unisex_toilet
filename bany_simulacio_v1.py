# Versió amb classe Employee però mètodes fora la classe

import threading
import time
import random

MEN = 6 # Nombre de processos home
WOMEN = 6 # Nombre processos dona
CAPACITY = 3 # Aforament màxim del bany (3 persones)

LADIES = ["Joana", "Marta", "Steph", "Carme", "Lidia", "Clara"]
GENTLEMEN = ["Joan", "Pere", "Mike", "Toni", "José", "Iván"]

MALE = 1
FEMALE = 2
EMPTY = 3

toilet = EMPTY # Inicialment buit
toilet_users=0

men_mutex = threading.Semaphore(1) # Per a bloquejar els processos home
women_mutex = threading.Semaphore(1) # Per a bloquejar els processos dona
lock = threading.Lock() # Mutex per les variables compartides pels processos home i dona
toilet_sem = threading.Semaphore(CAPACITY) # Màxim tres persones al bany al mateix temps

class Employee(object):
    def __init__(self, name, sex):
        self.name=name
        self.sex=sex

def man_toilet(persona, attempt):
    global toilet_users, toilet
    entered = False

    while not entered: # Intentará entrar fins que ho hagi aconseguit

        lock.acquire() # SC
        if toilet is FEMALE: # Si hi ha dones al bany
            lock.release()
            men_mutex.acquire()

        else: # Si no, vol dir que o bé està buit o bé ja hi ha homes al bany
            if toilet == EMPTY: toilet=MALE # Si està buit, ara serà pels homes        
            lock.release() 
            men_mutex.release()

            toilet_sem.acquire() # ---> Secció crítica (BANY)
                
            with lock:
                toilet_users+=1
                print("\x1b[1;32m  {} goes to the toilet ({}/2)- Current capacity: {} \x1b[0;37m".format(persona.name,attempt, toilet_users))
                                
            time.sleep(random.randint(5,20)/100) # Secció crítica (dins el bany)

            with lock:
                toilet_users-=1
                print("\x1b[1;32m  {} gets out the toilet - Current capacity: {} \x1b[0;37m".format(persona.name, toilet_users))
                if toilet_users==0:
                    print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
                    toilet=EMPTY
                    women_mutex.release()
            toilet_sem.release() # <---
                
            entered = True

def woman_toilet(persona, attempt):
    global toilet_users, toilet
    entered = False

    while not entered: # Intentará entrar fins que ho hagi aconseguit

        lock.acquire() # SC
        if toilet is MALE: # Si hi ha homes al bany
            lock.release()
            women_mutex.acquire()

        else: # Si no, vol dir que o bé està buit o bé ja hi ha dones al bany
            if toilet == EMPTY: toilet=FEMALE # Si està buit, ara serà per les dones        
            lock.release() 
            women_mutex.release()

            toilet_sem.acquire() # ---> Secció crítica (BANY)
                
            with lock:
                toilet_users+=1
                print("\x1b[1;34m  {} goes to the toilet ({}/2)- Current capacity: {} \x1b[0;37m".format(persona.name, attempt, toilet_users))
                                
            time.sleep(random.randint(50,200)/100) # Secció crítica (dins el bany)

            with lock:
                toilet_users-=1
                print("\x1b[1;34m  {} gets out the toilet - Current capacity: {} \x1b[0;37m".format(persona.name, toilet_users))
                if toilet_users==0:
                    print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
                    toilet=EMPTY
                    men_mutex.release()
            toilet_sem.release() # <---
                
            entered = True

def gets_to_work(persona):
    print("**** {} gets to the office ****".format(persona.name))
    time.sleep(random.randint(5,30)/10)

def works(persona):
    print("{} works ".format(persona.name))
    time.sleep(random.randint(5,30)/5)

def goes_home(persona):
    print("Bye {}".format(persona.name))

def goes_to_toilet(persona, attempt):
    if persona.sex is MALE:
        man_toilet(persona,attempt)
    else:
        woman_toilet(persona,attempt)

def run(persona):
    gets_to_work(persona)
    works(persona)
    goes_to_toilet(persona, 1) # First time
    works(persona)
    goes_to_toilet(persona, 2) # Second time
    goes_home(persona)

def main():
    threads = []

    for i in range(MEN):
        p = Employee(GENTLEMEN[i], MALE)
        t = threading.Thread(target=run, args=(p,))
        threads.append(t)

    for i in range(WOMEN):
        p = Employee(LADIES[i], FEMALE)
        t = threading.Thread(target=run, args=(p,))
        threads.append(t)

    # Start all threads
    for t in threads:
        t.start()

    # Wait for all threads to complete   
    for t in threads:
        t.join()

    print("End")

if __name__ == "__main__":
    main()