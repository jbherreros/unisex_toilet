# Versió amb clase Employee i un sol mètode per anar al bany (enlloc de 2, un per home i un per dona)

import threading
import time
import random

MEN = 6 # Nombre de processos home
WOMEN = 6 # Nombre processos dona
CAPACITY = 3 # Aforament màxim del bany (3 persones)

LADIES = ["Joana", "Marta", "Steph", "Carme", "Lidia", "Clara"]
GENTLEMEN = ["Joan", "Pere", "Mike", "Toni", "José", "Iván"]

MALE = 0
FEMALE = 1
EMPTY = 2

toilet = EMPTY # Inicialment buit **** Convé ficar això dins Employee?? JO CREC QUE SI
toilet_users=0

class Employee(threading.Thread):

    lock = threading.Lock() # Mutex per les variables compartides i garantir EM
    toilet_sem = threading.Semaphore(CAPACITY) # Màxim tres persones al bany al mateix temps
    sex_mutex = [] # Contendrà un mutex pels processos home i un pels processos dona

    def __init__(self, name, sex):
        super(Employee, self).__init__()
        self.name=name
        self.sex=sex
        self.sex_mutex.append(threading.Semaphore(1)) # Mutex per els homes
        self.sex_mutex.append(threading.Semaphore(1)) # Mutex per les dones

    def toilet(self, attempt):
        global toilet_users, toilet
        other_sex = self.opposite_sex() # Guarda el sexe oposat al de l'Employee actual
        entered = False

        while not entered: # Intentará entrar fins que ho hagi aconseguit

            Employee.lock.acquire()
            if toilet is other_sex: # Si l'altre sexe està al bany, el procés quedará bloquejat
                Employee.lock.release()
                Employee.sex_mutex[self.sex].acquire() 

            else: # Si no, vol dir que o bé està buit o o que el meu sexe està dins el bany
                if toilet == EMPTY: toilet=self.sex # Si està buit, ara serà pel sexe de l'Employee que vol entrar       
                Employee.lock.release() 
                Employee.sex_mutex[self.sex].release() # S'alliberen tots els procesos del mateix sexe bloquejats

                Employee.toilet_sem.acquire() # ---> Secció crítica (BANY)
                    
                with Employee.lock:
                    toilet_users+=1
                    self.print_sex("{} goes to the toilet ({}/2)- Current capacity: {} ".format(self.name,attempt, toilet_users))
                                    
                time.sleep(random.randint(5,20)/100) 

                # aqui ????

                Employee.toilet_sem.release() # <--- Fi secció crítica (BANY)

                # Això podria estar també dins el bany ????
                with Employee.lock:
                    toilet_users-=1
                    self.print_sex("{} gets out the toilet - Current capacity: {}".format(self.name, toilet_users))
                    if toilet_users==0:
                        print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
                        toilet=EMPTY
                        Employee.sex_mutex[other_sex].release()
                    
                entered = True

    def print_sex(self, texto):
        if self.sex is MALE:
            print("\x1b[1;32m  {} \x1b[0;37m".format(texto)) # Imprimeix en verd
        if self.sex is FEMALE:
            print("\x1b[1;34m  {} \x1b[0;37m".format(texto)) # Imprimeix en blau
   
    def opposite_sex(self):
        if self.sex is MALE:
            return FEMALE
        else:
            return MALE
    
    def gets_to_work(self):
        print("**** {} gets to the office ****".format(self.name))
        time.sleep(random.randint(5,30)/10)

    def works(self):
        print("{} works ".format(self.name))
        time.sleep(random.randint(5,30)/5)

    def home(self):
        print("Bye {}".format(self.name))

    def run(self):
        self.gets_to_work()
        self.works()
        self.toilet(1) # First time
        self.works()
        self.toilet(2) # Second time
        self.home()

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

    print("\nEnd")

if __name__ == "__main__":
    main()