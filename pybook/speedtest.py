import random
import timeit
from pybook import *

# this is for testing speed only
# currently only tests inserts, (no match, deletes..)
def speed_test():
    init_circ_array_size=1000 
    repeat=10000
    
    
    side=Side(is_ask=True,init_size=init_circ_array_size,level_increment=1)
    order_id=0
    total_time=0 

    # insert 
    for i in range(0,repeat):
        price= random.randint(1,init_circ_array_size) 
        qty = random.randint(1,100)
        order=Order(is_ask=True,order_id=order_id,price=price,qty=qty)
        order_id+=1
        #start measure
        start_time=time.time()
        side.insert(order)
        end_time=time.time()
        #end measure
        total_time+= end_time-start_time
    print("AVG insertion TIME in microsec:",total_time/repeat*1000000)

    # match (do not reduce or delete)
    total_time= 0
    for i in range(0,repeat): 
        price = random.randint(1,init_circ_array_size) 
        qty = random.randint(1,100)
        order = Order(is_ask=False,order_id=1,price=price,qty=qty)

        start_time=time.time()
        side.get_matching_orders(order)
        end_time=time.time() 
        total_time += end_time-start_time
    print("AVG matching TIME in microsec:",total_time/repeat*1000000)

    # now test delete
    total_time = 0 
    for i in range(0,order_id+1):
        start_time = time.time()
        side.delete(i) 
        end_time = time.time()
        total_time += end_time-start_time
    print("AVG deletion TIME in microsec:",total_time/repeat*1000000)

if __name__=='__main__':
    speed_test()
