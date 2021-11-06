# Versió amb classe Employee i tots els mètodes dins la classe

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

"""# ********************* Això ha d'estar dins la classe Employee ************************
men_mutex = threading.Semaphore(1) # Per a bloquejar els processos home
women_mutex = threading.Semaphore(1) # Per a bloquejar els processos dona
lock = threading.Lock() # Mutex per les variables compartides pels processos home i dona
toilet_sem = threading.Semaphore(CAPACITY) # Màxim tres persones al bany al mateix temps"""

class Employee(threading.Thread):

    sex_mutex = []
    men_mutex = threading.Semaphore(1) # Per a bloquejar els processos home
    women_mutex = threading.Semaphore(1) # Per a bloquejar els processos dona
    lock = threading.Lock() # Mutex per les variables compartides pels processos home i dona
    toilet_sem = threading.Semaphore(CAPACITY) # Màxim tres persones al bany al mateix temps

    def __init__(self, name, sex):
        super(Employee, self).__init__()
        self.name=name
        self.sex=sex

    def man_pees(self, attempt):
        global toilet_users, toilet
        entered = False
        other_sex = self.opposite_sex() # Guarda el sexe oposat al de l'Employee actual

        while not entered: # Intentará entrar fins que ho hagi aconseguit

            Employee.lock.acquire() # SC
            if toilet is FEMALE: # Si hi ha dones al bany
                Employee.lock.release()
                Employee.men_mutex.acquire()

            else: # Si no, vol dir que o bé està buit o bé ja hi ha homes al bany
                if toilet == EMPTY: toilet=MALE # Si està buit, ara serà pels homes        
                Employee.lock.release() 
                Employee.men_mutex.release()

                Employee.toilet_sem.acquire() # ---> Secció crítica (BANY)
                    
                with Employee.lock:
                    toilet_users+=1
                    print("\x1b[1;32m  {} goes to the toilet ({}/2)- Current capacity: {} \x1b[0;37m".format(self.name,attempt, toilet_users))
                                    
                time.sleep(random.randint(5,20)/100) # Secció crítica (dins el bany)

                with Employee.lock:
                    toilet_users-=1
                    print("\x1b[1;32m  {} gets out the toilet - Current capacity: {} \x1b[0;37m".format(self.name, toilet_users))
                    if toilet_users==0:
                        print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
                        toilet=EMPTY
                        Employee.women_mutex.release()
                Employee.toilet_sem.release() # <---
                    
                entered = True

    def woman_pees(self, attempt):
        global toilet_users, toilet
        entered = False

        while not entered: # Intentará entrar fins que ho hagi aconseguit

            Employee.lock.acquire() # SC
            if toilet is MALE: # Si hi ha homes al bany
                Employee.lock.release()
                Employee.women_mutex.acquire()

            else: # Si no, vol dir que o bé està buit o bé ja hi ha dones al bany
                if toilet == EMPTY: toilet=FEMALE # Si està buit, ara serà per les dones        
                Employee.lock.release() 
                Employee.women_mutex.release()

                Employee.toilet_sem.acquire() # ---> Secció crítica (BANY)
                    
                with Employee.lock:
                    toilet_users+=1
                    print("\x1b[1;34m  {} goes to the toilet ({}/2)- Current capacity: {} \x1b[0;37m".format(self.name, attempt, toilet_users))
                                    
                time.sleep(random.randint(50,200)/100) # Secció crítica (dins el bany)

                with Employee.lock:
                    toilet_users-=1
                    print("\x1b[1;34m  {} gets out the toilet - Current capacity: {} \x1b[0;37m".format(self.name, toilet_users))
                    if toilet_users==0:
                        print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
                        toilet=EMPTY
                        Employee.men_mutex.release()
                Employee.toilet_sem.release() # <---
                    
                entered = True
       
    def gets_to_work(self):
        print("**** {} gets to the office ****".format(self.name))
        time.sleep(random.randint(5,30)/10)

    def works(self):
        print("{} works ".format(self.name))
        time.sleep(random.randint(5,30)/5)

    def goes_to_toilet(self,attempt):
        if self.sex is MALE:
            self.man_pees(attempt)
        else:
            self.woman_pees(attempt)

    def goes_home(self):
        print("Bye {}".format(self.name))

    def run(self):
        self.gets_to_work()
        self.works()
        self.goes_to_toilet(1) # First time
        self.works()
        self.goes_to_toilet(2) # Second time
        self.goes_home()

def main():
    threads = []

    for i in range(MEN):
        threads.append(Employee(GENTLEMEN[i], MALE))

    for i in range(WOMEN):
        threads.append(Employee(LADIES[i], FEMALE))

    # Start all threads
    for t in threads:
        t.start()

    # Wait for all threads to complete   
    for t in threads:
        t.join()

    print("End")

if __name__ == "__main__":
    main()