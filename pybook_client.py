import pybook_config
import json
import sys
sys.path.append('../')
from cryptoutils import socketmsg


def get_book_config(pair):
    msg='config'
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)

def get_level_increment(pair):
    return pybook_config.CONFIG_DICT[pair]['level_increment']

def book_exists(instrument,unit):
    return (instrument,unit) in pybook_config.CONFIG_DICT
        
def submit_order(pair,order_id,price,qty,is_ask):
   
    if is_ask:#convert boolean to int
        is_ask=1
    else:
        is_ask=0

    msg=' '.join(['submit',str(order_id),str(price),str(qty),str(is_ask)])
  
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)

def delete_order(pair,order_id):
    msg=' '.join(['delete',str(order_id)])
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)

def get_state(pair):
    msg='state'
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)

def get_order(pair,order_id):
    msg='get_order'
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)


def clear_book(pair):
    msg='clear'
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)


def get_best_price(pair):
    msg='best_price'
    port=pybook_config.CONFIG_DICT[pair]['port']
    recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
    return json.loads(recvmsg)


# clears all book
def clear_all_book():
    msg='clear'
    out_list=[]
    for pair in pybook_config.CONFIG_DICT:
        port=pybook_config.CONFIG_DICT[pair]['port']
        recvmsg=socketmsg.communicate(pybook_config.TCP_IP,port,msg,pybook_config.BUFFER_SIZE)
        out_list.append(json.loads(recvmsg))



    return out_list

if __name__=='__main__':

    while 1:
        order_id=raw_input('order id:')
        instrument=raw_input('instrument:')
        unit=raw_input('unit:')
        price=raw_input('price:')
        qty=raw_input('qty:')
        is_ask=raw_input('is ask:')
        print submit_order((instrument,unit),order_id,price,qty,is_ask)
    s.close()


