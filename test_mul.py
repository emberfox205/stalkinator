from multiprocessing import Process
import time
import time
def update_token():
    #while True:
        print("Updating token...")
        time.sleep(10)
def get_coords():
    for _ in range(5):
        print("Getting coords...")
        time.sleep(2)
flag = False
if __name__ == "__main__":
    start_time = time.time()
    process1 = Process(target=update_token)
    process2 = Process(target=get_coords)
    process1.start()
    if not flag:
        time.sleep(1)
        flag = True
    process2.start()
    process1.join()
    process2.join()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("Finish time:", execution_time, "seconds")