import random
import timeit
from pybook import *

# this is for testing speed only
# currently only tests inserts, (no match, deletes..)
def speed_test():
    init_circ_array_size=1000 
    num_test_repeats=100
    num_insertions_per_repeat=1000
    
    
    side=Side(is_ask=True,init_size=init_circ_array_size,level_increment=1)
    order_id=0
    total_time=0 
    for i in range(0,num_insertions_per_repeat):
        price= random.randint(1,init_circ_array_size) 
        order=Order(is_ask=True,order_id=order_id,price=price,qty=1)
        order_id+=1
        #start measure
        start_time=time.time()
        side.insert(order)
        end_time=time.time()
        #end measure
        total_time+= end_time-start_time
    print("AVG insertion TIME in microsec:",total_time/num_insertions_per_repeat*1000000)


if __name__=='__main__':
    speed_test()
