# FEATURES - O(1) insert, 0(1) delete , 
# circular array. Each object in array is a dict of orders. 
# Each order is also in a hash table (python dict) for fast access, deletion 
import time
import json 
import logging 
import pybook_config
from collections import OrderedDict

class Order(object):
    def __init__(self,order_id,price,is_ask,qty=1,creation_time=0):
        self.order_id = order_id
        self.price = price 
        self.qty = qty
        self.is_ask = is_ask
        self.creation_time = creation_time
    def __repr__(self):
        return "order_id:{},price:{},qty:{},is_ask:{},creation_time:{}".format(
            self.order_id,self.price,self.qty,self.is_ask,self.creation_time)

class DeepOrders(object):
    def __init__(self,is_ask):
        # dict where key is (price,order_id) and value is Order 
        self.deep_orders={}
        self.is_ask=is_ask
    def __iter__(self):
        return self.deep_orders.__iter__()

    def __getitem__(self,key):
        return self.deep_orders[key]

    def __len__(self):
        return len(self.deep_orders)

    def delete(self,price,order_id):
        del self.deep_orders[(price,order_id)] 

    def contains(self,price,order_id):
        return (price,order_id) in self.deep_orders

    def insert(self,order):
        self.deep_orders[(order.price,order.order_id)]=order

    def get_best_price(self):
        if self.is_ask:    
            return min([self.deep_orders[key].price for key in self.deep_orders])
        else:
            return max([self.deep_orders[key].price for key in self.deep_orders])

    def get_sorted_order_list(self):
        unsorted_list=[self.deep_orders[key] for key in self.deep_orders]
        if self.is_ask: # return by lowest price first
            return sorted(unsorted_list, key=lambda x: (x.price,x.creation_time))
        else: # return by highest price first
            return sorted(unsorted_list, key=lambda x: (-x.price, x.creation_time))


class Level(object):
    def __init__(self):
        self.level=OrderedDict()

    def __iter__(self):
        return self.level.__iter__()

    def __getitem__(self,order_id):
        return self.level[order_id] 

    def __len__(self):
        return len(self.level)

    def __contains__(self,key):
        return key in self.level

    def delete(self,order_id):
        del self.level[order_id]

    def insert(self,order):
        self.level[order.order_id]=order

    # note that this will return orders sorted by insertion time, not
    # orders.creation_time 
    def values(self):         
        return self.level.values()

class Side(object):

    # is_ask            - if True, this is ask side of the book
    # init_size         - this is the size of circular array 
    # level_increment   - this is the steps in price between each level
    # deep_level_limit  - this prohibits the insertion of orders very deep in the book.
    #                       It can be None, if there is no limit. Canot be less than init_size 
    def __init__(self,is_ask,init_size,level_increment,deep_level_limit=None):

        self.is_ask=is_ask
        if deep_level_limit !=None and deep_level_limit<init_size:
            raise Exception("deep_level_limit cannot be less than init_size")  
        self.deep_level_limit=deep_level_limit
        
        self.circ_array=[Level() for i in range(init_size)]
        # start initial index (top of side) at the middle of circ_array
        # the index always refers to the top of the book
        self.top_index= init_size / 2 #note this is not compatible with python 3.0
        # each new level is at price +/- level_increment 
        self.level_increment=level_increment 
        # index_price is the price at index 
        self.top_index_price=None
        # the current number of levels occupied in ciculary array
        # level 0 (top of book) counts as a level
        self.num_levels=0
        self.num_orders=0
        
        self.deep_orders=DeepOrders(self.is_ask)
        #dict of all orders, this allows deletion or retrieval with just orderid
        self.all_orders={}

    def __repr__(self):
        if self.is_ask:
            str='Ask Side\n'
            loop_over=range(self._max_level_on_circ_array(),-1,-1)
        else:
            str='Bid Side\n'
            loop_over=range(0,self._max_level_on_circ_array()+1)
        if self.get_num_orders() == 0:
            str+='No Orders\n'
        else:
            for i in loop_over:
                if self.get_qty_at_level(i) != 0:
                    str+='Level:{},Price:{},Orders:{},Qty:{}\n'.format(
                            i,self.get_price_at_level(i),
                            self.get_num_orders_at_level(i),
                            self.get_qty_at_level(i))
            for order in self.deep_orders:
                str+='Level:Deep,Price:{},Qty:{}\n'.format(
                    self.deep_orders[order].price,
                    self.deep_orders[order].qty
                )
        return str
 
    def get_state(self):
        out=[]
        for i in range(0,self._max_level_on_circ_array()+1):
            if self.get_qty_at_level(i) != 0:
                cur_out={'level':i, 'price':self.get_price_at_level(i),
                         'orders':self.get_num_orders_at_level(i), 'qty':self.get_qty_at_level(i)}
                out.append(cur_out)
        for order in self.deep_orders:
            self.deep_orders[order]
            cur_out={'level':-1,'price':self.deep_orders[order].price,'qty':self.deep_orders[order].qty}
            out.append(cur_out)   
        return out

    # return list of orders at level
    def get_orders_at_level(self,level):
        index=self.get_index_at_level(level)
        return self.circ_array[index].values()

    def get_num_orders_at_level(self,level):
        if level < 0:
            self.logger.critical('Level cannot be less than zero for get_num_orders_at_level()') 
            raise Exception('Level cannot be less than zero for get num_orders_at_level()')
        return len(self.circ_array[self.get_index_at_level(level)])

    def get_qty_at_level(self,level):
        circ_array_index=self.get_index_at_level(level)
        a= [self.circ_array[circ_array_index][order_id].qty for order_id in self.circ_array[circ_array_index]]
        return sum(a)

    def get_num_orders(self):
        return self.num_orders

    def get_num_deep_orders(self):
        return len(self.deep_orders)

    def get_num_circ_aray_orders(self):
        return self.get_num_orders() - self.get_num_deep_orders()

    def get_order(self,order_id):
        if order_id in self.all_orders:
            return self.all_orders[order_id]
        else:
            return None


    # return matching orders as list  of 
    # (order_id, order_qty,qty_to_take)            
    def get_matching_orders(self,order):
        matching_orders_out=[]
        if order.is_ask == self.is_ask:
            raise Exception('order for get_matching_orders cannot be on the same side')
        if self.get_num_orders() ==0:
            return [] 
        if self.is_ask==True and order.price < self.get_price_at_level(0):
            return [] 
        if self.is_ask==False and order.price > self.get_price_at_level(0):
            return []
            
        max_level   = min(self._max_level_on_circ_array(), self.get_level_at_price(order.price))
        matched_qty = 0
        # first check circ_array
        for i in range(0,max_level+1):
            orders_at_level=self.get_orders_at_level(i)
            for cur_order in orders_at_level:
                if matched_qty+cur_order.qty <=order.qty: #fully take
                    matching_orders_out.append((cur_order.order_id,cur_order.qty,cur_order.qty)) 
                    matched_qty += cur_order.qty
                else: # partially take
                    reduce_qty = order.qty - matched_qty  
                    matching_orders_out.append((cur_order.order_id,cur_order.qty,reduce_qty))
                    matched_qty += cur_order.qty
                    break
                if matched_qty >=order.qty:
                    break

            if matched_qty >= order.qty:
                    break
        
        # than check deep orders if necessary
        if matched_qty < order.qty:
            order_list=self.deep_orders.get_sorted_order_list()
            for cur_order in order_list:
                if self.is_ask==True and cur_order.price <= order.price:
                    break
                elif self.is_ask==False and cur_order.price >= order.price: 
                    break
                else:
                    if matched_qty+cur_order.qty <= order.qty:
                        matching_orders_out.append((cur_order.order_id,cur_order.qty,cur_order.qty)) 
                        matched_qty+=cur_order.qty 
                    else:
                        reduce_qty = matched_qty + cur_order.qty - order.qty 
                        matching_orders_out.append((cur_order.order_id,cur_order.qty,reduce_qty))
                        matched_qty += cur_order.qty
                        break
               
        return matching_orders_out

    # reduce order qty. Remove order if qty is zero 
    def reduce(self,order_id,reduce_qty):
        if order_id not in self.all_orders:
            return (False, 'order_id not found')

        if reduce_qty > self.all_orders[order_id].qty:
            return (False, 'cannot reduce more than  available qty')
        elif reduce_qty < self.all_orders[order_id].qty:
            self.all_orders[order_id].qty-=reduce_qty
            return (True,'')
        else: # qty is equal
            self.delete(order_id) 
            return (True,'')

    # delete order, order must contain order_id and price 
    def delete(self,order_id):
        if order_id not in self.all_orders:
            return (False, 'order_id {} to delete not found'.format(order_id))

        price=self.all_orders[order_id].price         
        index=self.get_index_at_price(price)
        if index != None and order_id in self.circ_array[index]:
            self.circ_array[index].delete(order_id)
            del self.all_orders[order_id]
            self.num_orders -= 1
            if self.num_orders == 0:
                self.top_index_price = None
                self.num_levels=0
                return (True,'')
        elif self.deep_orders.contains(price,order_id):
            self.deep_orders.delete(price,order_id)
            del self.all_orders[order_id]
            self.num_orders -=1
            if self.num_orders == 0: 
                # shouldn't reach here, as if we delete from deep orders, 
                # there must always be something in circ_array
                self.top_index_price = None
                self.num_levels=0
            return (True,'')
        else:
            return (False,'order_id found in all_orders but not anywhere else')

        # no more order in level and it is top of book
        # need to update the top of book 
        if len(self.circ_array[index])==0 and index==self.top_index:

            next_full_level=None
            # find next full level
            for i in range(1,self._max_level_on_circ_array()+1):
                if self.get_num_orders_at_level(i) > 0:
                    next_full_level=i
                    break
            if next_full_level == None: #there is no more order in circ_array 
                self.top_index_price = self.deep_orders.get_best_price()
                self.num_levels = 0

            else:
                new_top_index=self.get_index_at_level(next_full_level)
                new_top_index_price= self.get_price_at_level(next_full_level)
                self.top_index =  new_top_index
                self.top_index_price = new_top_index_price
                self.num_levels -= next_full_level
            

        # no more order in level and it is bottom of book   
        elif len(self.circ_array[index])==0 and index==self.get_index_at_level(self.num_levels-1):
            self.num_levels -=1

        #whenever we delete levels, look in deep orders to see if we can add it back to circ_array 
        # this is kind of inefficient , we can use a heap or something here 
        keys_to_delete=[]
        for key in self.deep_orders:
            deep_order_price = key[0]
            if self.get_level_at_price(deep_order_price) <= self._max_level_on_circ_array():
                self._insert(self.deep_orders[key])
                keys_to_delete.append(key)

        for key in keys_to_delete:
            self.deep_orders.delete(key[0],key[1])
   
        return (True,'')

    def insert(self,order):
        if order.order_id in self.all_orders:
            return (False,'order_id {} exists already'.format(order.order_id))
        if self.deep_level_limit != None and self.get_num_orders()!=0 and self.get_level_at_price(order.price) >= self.deep_level_limit: 
            return (False, 'order_too_deep')
        if order.price % self.level_increment != 0:
            return (False, 'order price fails level_increment')
        if order.is_ask != self.is_ask:
            return (False, 'order side is different')
        if order.price <=0:
            return (False, 'price cannot be equal to or less than zero')
        if order.qty <=0:
            return (False, 'quantity cannot be equal to or less than zero') 
        self._insert(order)
        self.all_orders[order.order_id]=order
        self.num_orders +=1       
        return (True,'')

    def _insert(self,order): 
        order_id=order.order_id 
        price=order.price
        # if this is first order being inserted
        if self.top_index_price==None:
            self.circ_array[self.top_index].insert(order)
            self.num_levels+=1
            self.top_index_price=price

        # otherwise
        else:
            insert_level=self.get_level_at_price(price)
            # we need to put it in deep_orders
            if insert_level > self._max_level_on_circ_array():
                self.deep_orders.insert(order)#[(price,order_id)]=order 
            # we need to clear up space in circ_array and move them to deep orders 
            elif insert_level < self._min_level_on_circ_array():
                levels_to_clear = - (insert_level - self._min_level_on_circ_array())
                for i in range(0,levels_to_clear):
                    tmp_index= self.get_index_at_level(self.num_levels -1-i)
                    for key in self.circ_array[tmp_index]:
                        move_order=self.circ_array[tmp_index][key] 
                        self.deep_orders.insert(move_order) #[(move_order.price,move_order.order_id)]=move_order
                    
                    self.circ_array[tmp_index]=Level()
                self.circ_array[self.get_index_at_level(insert_level)].insert(order)

                self.top_index = self.get_index_at_level(insert_level)
                self.top_index_price = price
            # we can insert
            else:
                self.circ_array[self.get_index_at_level(insert_level)].insert(order)
                if insert_level < 0:
                    self.top_index          = self.get_index_at_level(insert_level)
                    self.top_index_price    = price
                    self.num_levels         += abs(insert_level)
                else:
                    self.num_levels         = max(self.num_levels,insert_level+1) 


    def _max_level_on_circ_array(self):
        return len(self.circ_array)-1
    
    def _min_level_on_circ_array(self):
        return -len(self.circ_array) + self.num_levels

    # get index to circ array at price, if this exceeds available
    # circ_array size, return None
    def get_index_at_price(self,price):
    
        price_diff = price - self.top_index_price
        level_diff = price_diff / self.level_increment
        if(abs(level_diff) >= len(self.circ_array)):
            return None
        if not self.is_ask:
            level_diff=-level_diff

        insert_index= ( self.top_index+level_diff )%len(self.circ_array)
        return insert_index

    def get_index_at_level(self,level):
        
        return (self.top_index+level) % len(self.circ_array)

    # get price at level, if level does not exist , return None
    def get_price_at_level(self,level):
        if not self.is_ask: 
            level=-level
        if self.top_index_price == None:
            return None 

        return self.top_index_price + (level*self.level_increment)
        
    def get_level_at_price(self,price): 
        # must now return none eve if level is past circ_array
        # since this function is used to compute how deep the
        # order will be
        price_diff = price - self.top_index_price
        level_diff = price_diff / self.level_increment       
        if self.is_ask:
            return level_diff
        else:
            return -level_diff
     

class Book(object):

    def __init__(self,init_size,level_increment,
                 qty_increment = None, instrument = None, unit = None,
                 min_price = None, max_price = None, min_qty = None, max_qty = None,
                 deep_level_limit = None):

        self.init_size          = init_size
        self.level_increment    = level_increment
        self.instrument         = instrument
        self.unit               = unit
        self.deep_level_limit   = deep_level_limit

        if qty_increment!=None and qty_increment<=0:
            raise Exception('qty_increment must be greater than zero')
        self.qty_increment=qty_increment
 
        if min_price!=None and min_price <=0:
            raise Exception('min_price must be greater than zero')
        self.min_price=min_price
        if min_price!=None and max_price <=0:
            raise Exception('max_price must be greater than zero')
        self.max_price=max_price       

        if min_qty!= None and min_qty <=0:
            raise Exception('min_qty must be greater than zero')
        self.min_qty=min_qty
        if max_qty!= None and max_qty <=0:
            raise Exception('max_qty must be greater than zero')
        self.max_qty=max_qty


        self.ask_side   = Side(is_ask=True,init_size=self.init_size,level_increment=self.level_increment,deep_level_limit=deep_level_limit)
        self.bid_side   = Side(is_ask=False,init_size=self.init_size,level_increment=self.level_increment,deep_level_limit=deep_level_limit)

        # setup logger

        self.logger = logging.getLogger('pybook')
        self.logger.setLevel(logging.WARN)
        time_string = time.strftime('%Y-%m-%d-%H-%M-%S')
        file_handler = logging.FileHandler('{}_{}_pybook_{}.pylog'.format(instrument,unit,time_string))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter) 
        self.logger.addHandler(file_handler)

    @classmethod
    def from_pybook_config(cls,instrument,unit):
        pair=(instrument,unit) 

        port                = pybook_config.CONFIG_DICT[pair]['port']
        level_increment     = pybook_config.CONFIG_DICT[pair]['level_increment']
        qty_increment       = pybook_config.CONFIG_DICT[pair]['qty_increment']
        init_size           = pybook_config.CONFIG_DICT[pair]['init_size']
        deep_level_limit    = pybook_config.CONFIG_DICT[pair]['deep_level_limit']
         
        min_price           = pybook_config.CONFIG_DICT[pair]['min_price']
        max_price           = pybook_config.CONFIG_DICT[pair]['max_price']

        min_qty             = pybook_config.CONFIG_DICT[pair]['min_qty']
        max_qty             = pybook_config.CONFIG_DICT[pair]['max_qty']


        return cls(init_size=init_size,level_increment=level_increment,
              qty_increment=qty_increment,instrument=instrument,unit=unit,
              min_price=min_price,max_price=max_price,min_qty=min_qty,max_qty=max_qty,
              deep_level_limit=deep_level_limit)
         

    def __repr__(self):
        out=''
        out += self.ask_side.__repr__()
        out += self.bid_side.__repr__()
        return out

    # process and return message
    def process_msg(self,msg):
        msg_list=msg.split()
        self.logger.info('processing msg: '+msg)
        if len(msg_list) == 0:
            out_json['success']=0
            out_json['result']='invalid_command'
            return json.dumps(out_json)
        out_json={}
        if msg_list[0]=='submit':
            if len(msg_list) == 5:
                order=Order(order_id=int(msg_list[1]),price=int(msg_list[2]),qty=int(msg_list[3]),is_ask=int(msg_list[4]))
            else:
                out_json['success']=0
                out_json['result']='parameter_error'
                return json.dumps(out_json)
                
            submit_result=self.submit_order(order)
            if submit_result[0]==True:
                out_json['success']=1 
                out_json['result']=submit_result[1] 
                
            else:
                out_json['success']=0
                out_json['result']=submit_result[1]
            return json.dumps(out_json)

        elif msg_list[0]=='delete':
            if len(msg_list) != 2:
                out_json['success']=0
                out_json['result']='delete_parameter_error'
                return json.dumps(out_json)
            delete_result=self.delete_order(int(msg_list[1]))
            if delete_result[0]==True:
                out_json['success']=1
                return json.dumps(out_json)
            else:
                out_json['success']=0
                out_json['result']=delete_result[1]
                return json.dumps(out_json) 

        elif msg_list[0]=='state':
            if len(msg_list) != 1:
                out_json['success']=0
                out_json['result']='state_parameter_error'
                return out_json
            out_json['success']=1

            ask_state=self.ask_side.get_state()
            bid_state=self.bid_side.get_state()
            out_json['result']={'ask':ask_state,'bid':bid_state}

            return json.dumps(out_json) 
    
        elif msg_list[0]=='best_price':
            if len(msg_list) != 1:
                out_json['success']=0
                out_json['result']='bbo_parameter_error'
                return out_json
            out_json['success']=1
            best_ask=self.ask_side.get_price_at_level(0)
            best_bid=self.bid_side.get_price_at_level(0)
            out_json['result']={'best_ask':best_ask,'best_bid':best_bid}
            return json.dumps(out_json)

        elif msg_list[0]=='clear':
            self.clear()
            out_json['success']=1
            return json.dumps(out_json)

        elif msg_list[0]=='config':
            out_json['success']=1
            out_json['result']={
                'init_size':self.init_size,'level_increment':self.level_increment,
                'qty_increment':self.qty_increment,'instrument':self.instrument,'unit':self.unit,
                'min_price':self.min_price,'max_price':self.max_price,'min_qty':self.min_qty,'max_qty':self.max_qty,
                'deep_level_limit':self.deep_level_limit}
            return json.dumps(out_json)
        elif msg_list[0]=='get_order':
            order_id=int(msg_list[1])
            result=self.get_order(order_id)
            out_json['success']=1
            out_json['result']=result
            return json.dumps(out_json)
        else: 
            return 'error invalid_command' 

    # retreive order by order_id, return None if it does not exist
    def get_order(self,order_id):
        order=self.ask_side.get_order(order_id)
        if order == None:
            return self.bid_side.get_order(order_id)
        else:
            return order
    # clear both sides of all orders
    def clear(self):
        self.ask_side=Side(is_ask=True,init_size=self.init_size,level_increment=self.level_increment,
                           deep_level_limit=self.deep_level_limit)
        self.bid_side=Side(is_ask=False,init_size=self.init_size,level_increment=self.level_increment,
                           deep_level_limit=self.deep_level_limit)

    # reduce order
    def reduce_order(self,order_id,reduce_qty):
        order_id_in_ask=order_id in self.ask_side.all_orders
        order_id_in_bid=order_id in self.bid_side.all_orders
        if order_id_in_ask and order_id_in_bid:
            return (False,'order_id {} in both ask side and bid side'.format(order_id))
        if not (order_id_in_ask or order_id_in_bid):
            return (False,'order_id {} not found in either bid or ask'.format(order_id))

        if order_id_in_ask:
            side = self.ask_side
        else:
            side = self.bid_side
        return side.reduce(order_id,reduce_qty)
      

    # remove order 
    def delete_order(self,order_id):
        order_id_in_ask=order_id in self.ask_side.all_orders
        order_id_in_bid=order_id in self.bid_side.all_orders
        if order_id_in_ask and order_id_in_bid:
            return (False,'order_id {} in both ask side and bid side'.format(order_id))
        if not (order_id_in_ask or order_id_in_bid):
            return (False,'order_id {} not found in either bid or ask'.format(order_id))

        if order_id_in_ask:
            side = self.ask_side
        else:
            side = self.bid_side
        return side.delete(order_id)

    def submit_order(self,order):

        # perform qty/price checks 
        if self.min_qty != None and order.qty < self.min_qty:
            return (False, 'quantity cannot be less than min qty:'+self.min_qty)
        if self.max_qty != None and order.qty > self.max_qty:
            return (False, 'quantity cannot be more than max qty:'+self.max_qty)
        if self.min_price != None and order.price < self.min_price:
            return (False, 'price cannot be less than min price:'+self.min_price)
        if self.max_price != None and order.price > self.max_price:
            return (False, 'price cannot be more than max price:'+self.max_price)
        if self.qty_increment != None and order.qty % self.qty_increment != 0:
            return(False, 'qty fails qty_increment')

        out_dict={'created':[],'taken':[]}
        total_matched_qty=0

        if order.is_ask:
            matching_orders=self.bid_side.get_matching_orders(order)
            side=self.ask_side
            opposite_side=self.bid_side
        else:
            matching_orders=self.ask_side.get_matching_orders(order)
            side=self.bid_side
            opposite_side=self.ask_side
        if len(matching_orders)!=0:
            for match in matching_orders:
                order_id=match[0]
                order_qty=match[1]
                taken_qty=match[2]
                total_matched_qty+=taken_qty
                out_dict['taken'].append({'order_id':order_id,'qty':taken_qty})
                if order_qty == taken_qty:
                    result=opposite_side.delete(order_id)                    
                    if result[0]==False:
                        msg='Failed to delete order {}: {}'.format(order_id,result[1])
                        self.logger.critical(msg)
                        return(False,msg)
                    else:
                        msg='Deleted order_id {}'.format(order_id)
                        self.logger.info(msg)
                else:
                    result=opposite_side.reduce(order_id,taken_qty)
                    if result[0]==False:       
                        msg='Failed to reduce an order: '+result[1]
                        self.logger.critical(msg)
                        return(False,msg)
                    else:
                        msg='Reduced order_id {} by {}'.format(order_id,taken_qty)
                        self.logger.info(msg)

        if total_matched_qty < order.qty:
 
            order.qty -= total_matched_qty
            result=side.insert(order) 
            if result[0]==True:
                out_dict['created'].append({'order_id':order.order_id,'qty':order.qty})
                msg='Created order, order id:{} qty:{} price:{} is_ask:{}'.format(order.order_id,order.qty,order.price,order.is_ask) 
                self.logger.info(msg)
            else:
                msg='Failed to insert order({}): {}'.format(str(order),result[1])
                self.logger.critical(msg) 
                return(False,msg) 

        
        return (True,out_dict)           

if __name__=='__main__':
    book=Book(init_size=5,level_increment=1)
    while 1:
        msg=raw_input('enter command (h for help) :')
        if msg=='h':
            print("submit (order_id) (price) (qty) (is_ask) \n delete (order_id) ")
        else:
            result=book.process_msg(msg)
            print(result)
            print(book)


