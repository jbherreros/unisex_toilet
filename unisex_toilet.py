# Juan Carlos Bujosa Herreros and José Luis García Herreros
import threading, time, random

MEN = 6 # Nombre de processos home
WOMEN = 6 # Nombre processos dona
MAX_CAPACITY = 3 # Aforament màxim del bany (3 persones)

LADIES = ["Joana", "Marta", "Steph", "Carme", "Lidia", "Clara"]
GENTLEMEN = ["Joan", "Pere", "Mike", "Toni", "José", "Iván"]

toilet_users = 0
MALE = 1
FEMALE = 2

queue = threading.Lock() # Mutex per simular la cua de entrada al bany
man_m = threading.Lock() # Mutex home
woman_m = threading.Lock() # Mutex dona
toilet_sem = threading.Semaphore(MAX_CAPACITY) # Semàfor del bany
l = []

class Employee(object):
    def __init__(self, name, sex):
        self.name=name
        self.sex=sex

def toilet_woman(persona, attempt):
    global toilet_users

    #l.append(persona.name)
    #print("Toilet queue ", l)
    with queue:
        with woman_m:
            #l.pop(0)
            if (toilet_users==0):
                man_m.acquire()

    toilet_sem.acquire()    
    with woman_m:
        toilet_users+=1
        print("\x1b[1;32m  {} gets into the toilet ({}/2)- Current capacity: {} \x1b[0;37m".format(persona.name, attempt, toilet_users))   
    
    time.sleep(random.randint(50,200)/100) # Secció crítica (dins el bany)
    toilet_sem.release()

    with woman_m:
        toilet_users-=1
        print("\x1b[1;32m  {} gets out the toilet - Current capacity: {} \x1b[0;37m".format(persona.name, toilet_users))
        if toilet_users==0:
            print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
            man_m.release()


def toilet_man(persona, attempt):
    global toilet_users

    #l.append(persona.name)
    #print("Toilet queue ", l)
    with queue:
        with man_m:
            #l.pop(0)
            if (toilet_users==0):
                woman_m.acquire()

    toilet_sem.acquire()
    with man_m:
        toilet_users+=1
        print("\x1b[1;34m  {} gets into the toilet ({}/2)- Current capacity: {} \x1b[0;37m".format(persona.name, attempt, toilet_users))    
    time.sleep(random.randint(50,200)/100) # Secció crítica (dins el bany)
    toilet_sem.release()

    with man_m:
        toilet_users-=1
        print("\x1b[1;34m  {} gets out the toilet - Current capacity: {} \x1b[0;37m".format(persona.name, toilet_users))
        if toilet_users==0:
            print("\x1b[1;31m"+"****************** Toilet is empty ******************"+"\x1b[0;37m")
            woman_m.release()

def toilet(persona, attempt):
    if persona.sex==MALE:
        toilet_man(persona, attempt)
    else:
        toilet_woman(persona, attempt)

def gets_to_work(persona):
    print("**** {} gets to the office ****".format(persona.name))
    time.sleep(random.randint(5,50)/10)

def works(persona):
    print("{} works ".format(persona.name))
    time.sleep(random.randint(5,50)/5)

def goes_home(persona):
    print("Bye {}".format(persona.name))

def run(persona):
    gets_to_work(persona)
    works(persona)
    toilet(persona, 1) # First time
    works(persona)
    toilet(persona, 2) # Second time
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