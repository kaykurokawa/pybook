import time
import unittest
import json
import csv
from pybook import *

# read csv file with book command and state 
class TestBook_Params(unittest.TestCase):
    def setUp(self):
        pass
    def test_basic(self):
        book=Book(init_size=10,level_increment=1)

        f= open('booktest_params.txt','r')
        for line in f:
            csvs=line.split(';')
            msg=csvs[0]
            bid_state=json.loads(csvs[1])
            ask_state=json.loads(csvs[2])
            book.process_msg(msg)
            
            level=0
            for state in bid_state:
                price=state[0]
                qty=state[1]
                self.assertEqual(book.bid_side.get_qty_at_level(level),qty)
                self.assertEqual(book.bid_side.get_price_at_level(level),price)
                level+=1
            level=0
            for state in ask_state:
                price=state[0]
                qty=state[1]
                self.assertEqual(book.ask_side.get_qty_at_level(level),qty)
                self.assertEqual(book.ask_side.get_price_at_level(level),price)
                level+=1


class TestBook(unittest.TestCase):
    def setUp(self):
        pass
    
        
    def test_basic(self):
        book=Book(init_size=4,level_increment=1)
        order=Order(is_ask=True,price=5,qty=1,order_id=0)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1 ,len(out[1]['created']))
        self.assertEqual(0 ,out[1]['created'][0]['order_id'])
        self.assertEqual(1 ,out[1]['created'][0]['qty'])
        self.assertEqual(1,book.ask_side.get_num_orders())
        self.assertEqual(0,book.bid_side.get_num_orders())
        # fully take
        order=Order(is_ask=False,price=5,qty=1,order_id=1)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1,len(out[1]['taken']))
        self.assertEqual(0, out[1]['taken'][0]['order_id'])
        self.assertEqual(1, out[1]['taken'][0]['qty'])
       
        # double fill
        order=Order(is_ask=False,price=3,qty=1,order_id=2)
        out=book.submit_order(order)
        self.assertEqual(True,out[0]) 
        self.assertEqual(1,len(out[1]['created']))
        self.assertEqual(2,out[1]['created'][0]['order_id'])
        self.assertEqual(1,out[1]['created'][0]['qty'])
        self.assertEqual(0,book.ask_side.get_num_orders())
        self.assertEqual(1,book.bid_side.get_num_orders())

        order=Order(is_ask=False,price=2,qty=1,order_id=3)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1,len(out[1]['created']))
        self.assertEqual(3,out[1]['created'][0]['order_id'])
        self.assertEqual(1,out[1]['created'][0]['qty'])
        self.assertEqual(0,book.ask_side.get_num_orders())
        self.assertEqual(2,book.bid_side.get_num_orders())

        order=Order(is_ask=True,price=2,qty=2,order_id=4)
        out=book.submit_order(order)
     
        self.assertEqual(True,out[0])
        self.assertEqual(2,len(out[1]['taken']))
        self.assertEqual(0,len(out[1]['created']))

        self.assertEqual(2,out[1]['taken'][0]['order_id'])
        self.assertEqual(1,out[1]['taken'][0]['qty'])
        self.assertEqual(3,out[1]['taken'][1]['order_id'])
        self.assertEqual(1,out[1]['taken'][1]['qty'])

        self.assertEqual(0, book.bid_side.get_num_orders())  
        self.assertEqual(0, book.ask_side.get_num_orders())  

        # test delete 
        order=Order(is_ask=False,price=3,qty=1,order_id=5)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        
        out=book.delete_order(5)
        self.assertEqual(True,out[0])
        self.assertEqual(0, book.bid_side.get_num_orders())  


        #double filll with parital fill 
        order=Order(is_ask=False,price=3,qty=2,order_id=2)
        out=book.submit_order(order)

        order=Order(is_ask=False,price=2,qty=2,order_id=3)
        out=book.submit_order(order)

        order=Order(is_ask=True,price=2,qty=3,order_id=4)
        out=book.submit_order(order)
     
        self.assertEqual(True,out[0])
        self.assertEqual(2,len(out[1]['taken']))
        self.assertEqual(0,len(out[1]['created']))

        
        self.assertEqual(2,out[1]['taken'][0]['order_id'])
        self.assertEqual(2,out[1]['taken'][0]['qty'])
        self.assertEqual(3,out[1]['taken'][1]['order_id'])
        self.assertEqual(1,out[1]['taken'][1]['qty'])

        self.assertEqual(1, book.bid_side.get_num_orders())  
        self.assertEqual(0, book.ask_side.get_num_orders())  


        #fill with 1 created and 1 taken
        order=Order(is_ask=True,price=2,qty=3,order_id=5)
        out=book.submit_order(order)
  
     
        self.assertEqual(True,out[0])
        self.assertEqual(1,len(out[1]['taken']))
        self.assertEqual(1,len(out[1]['created']))

        self.assertEqual(3,out[1]['taken'][0]['order_id'])
        self.assertEqual(1,out[1]['taken'][0]['qty'])
        self.assertEqual(5,out[1]['created'][0]['order_id'])
        self.assertEqual(2,out[1]['created'][0]['qty'])


    def test_basic_2(self):
        book=Book(init_size=4,level_increment=1)
        order=Order(is_ask=True,price=5,qty=3,order_id=0)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1 ,len(out[1]['created']))
        self.assertEqual(0 ,out[1]['created'][0]['order_id'])
        self.assertEqual(3 ,out[1]['created'][0]['qty'])
        self.assertEqual(1,book.ask_side.get_num_orders())
        self.assertEqual(0,book.bid_side.get_num_orders())
        # partial non-half fill
        order=Order(is_ask=False,price=5,qty=2,order_id=1)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1,len(out[1]['taken']))
        self.assertEqual(0, out[1]['taken'][0]['order_id'])
        self.assertEqual(2, out[1]['taken'][0]['qty'])
        self.assertEqual(0, len(out[1]['created']))

    #  test partial fill when there are multiple orders at a level
    def test_partial_fill_with_multiple_orders(self):

        book=Book(init_size=4,level_increment=1)
        order=Order(0,10,True,2)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1 ,len(out[1]['created']))
        self.assertEqual(0 ,out[1]['created'][0]['order_id'])
        self.assertEqual(2 ,out[1]['created'][0]['qty'])
        self.assertEqual(1,book.ask_side.get_num_orders())
        self.assertEqual(0,book.bid_side.get_num_orders())

        order=Order(1,10,True,2)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1 ,len(out[1]['created']))
        self.assertEqual(1 ,out[1]['created'][0]['order_id'])
        self.assertEqual(2 ,out[1]['created'][0]['qty'])
        self.assertEqual(2,book.ask_side.get_num_orders())
        self.assertEqual(0,book.bid_side.get_num_orders())

        order=Order(2,10,True,2)
        out=book.submit_order(order)
        self.assertEqual(True,out[0])
        self.assertEqual(1 ,len(out[1]['created']))
        self.assertEqual(2 ,out[1]['created'][0]['order_id'])
        self.assertEqual(2 ,out[1]['created'][0]['qty'])
        self.assertEqual(3,book.ask_side.get_num_orders())
        self.assertEqual(0,book.bid_side.get_num_orders())
 
        order=Order(3,10,False,3)
        out=book.submit_order(order)           
        self.assertEqual(True,out[0])
        self.assertEqual(2 ,len(out[1]['taken']))
        self.assertEqual(0 ,out[1]['taken'][0]['order_id'])
        self.assertEqual(2 ,out[1]['taken'][0]['qty'])
        self.assertEqual(1 ,out[1]['taken'][1]['order_id'])
        self.assertEqual(1 ,out[1]['taken'][1]['qty'])
        self.assertEqual(2,book.ask_side.get_num_orders())
        self.assertEqual(0,book.bid_side.get_num_orders())
        self.assertEqual(3,book.ask_side.get_qty_at_level(0))

 

    def test_process_msg(self):
        book=Book(init_size=4,level_increment=1) 
        msg='submit 1 10 1 1'
        out=book.process_msg(msg)
        out=json.loads(out)
        self.assertEqual(1,out['success'])
        self.assertEqual(1,out['result']['created'][0]['order_id'])

        self.assertEqual(1, book.ask_side.get_num_orders())
        msg='submit 2 8 1 0'
        out=book.process_msg(msg)
        out=json.loads(out)
        self.assertEqual(1,out['success'])
        self.assertEqual(2,out['result']['created'][0]['order_id'])
        self.assertEqual(1, book.bid_side.get_num_orders())

 
# Unit test for test client
class TestSide(unittest.TestCase):
    def setUp(self):
        pass
     
    # test to see if when we delete a side to empty, we have issues
    def test_delete_to_empty(self):
         side=Side(is_ask=True,init_size=4,level_increment=1)
         order=Order(order_id=0,price=5,is_ask=True,qty=1)
         side.insert(order)
         side.delete(0)
         self.assertEqual(0, side.get_num_orders())
         self.assertEqual(0, side.get_num_deep_orders())

         side=Side(is_ask=False,init_size=4,level_increment=1)
         order=Order(order_id=0,price=5,is_ask=False,qty=1)
         side.insert(order)
         side.delete(0)
         self.assertEqual(0, side.get_num_orders())
         self.assertEqual(0, side.get_num_deep_orders())

    def test_basic_bid(self):
         side=Side(is_ask=False,init_size=4,level_increment=1)
         order=Order(order_id=0,price=5,is_ask=False,qty=1)
         side.insert(order)
         self.assertEqual(5,side.get_order(order_id=0).price)
         self.assertEqual(0,side.get_order(order_id=0).order_id)
         self.assertEqual(5,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders()) 
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(5,side.get_price_at_level(0))

         order=Order(order_id=1,price=3,is_ask=False,qty=1)
         side.insert(order)
         self.assertEqual(3,side.get_order(order_id=1).price)
         self.assertEqual(1,side.get_order(order_id=1).order_id)
         self.assertEqual(2,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(5,side.get_price_at_level(0))
         self.assertEqual(0,side.get_num_orders_at_level(1))
         self.assertEqual(4,side.get_price_at_level(1))
         self.assertEqual(1,side.get_num_orders_at_level(2))
         self.assertEqual(3,side.get_price_at_level(2))


         order=Order(order_id=2,price=6,is_ask=False,qty=1)
         side.insert(order)

         self.assertEqual(6,side.get_order(order_id=2).price)
         self.assertEqual(2,side.get_order(order_id=2).order_id)
         self.assertEqual(6,side.get_price_at_level(0))
         self.assertEqual(3,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(6,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(5,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(3,side.get_price_at_level(3))


         order=Order(order_id=3,price=2,is_ask=False,qty=1)
         side.insert(order)
         self.assertEqual(2,side.get_order(order_id=3).price)
         self.assertEqual(3,side.get_order(order_id=3).order_id)
         self.assertEqual(6,side.get_price_at_level(0))
         self.assertEqual(4,side.get_num_orders())
         self.assertEqual(1,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(6,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(5,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(3,side.get_price_at_level(3))


         # test deletion from circ_array
         side.delete(2)
         self.assertEqual(3,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(5,side.get_price_at_level(0))
         self.assertEqual(0,side.get_num_orders_at_level(1))
         self.assertEqual(4,side.get_price_at_level(1))
         self.assertEqual(1,side.get_num_orders_at_level(2))
         self.assertEqual(3,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(2,side.get_price_at_level(3))

                       
         order=Order(order_id=4,price=1,is_ask=False,qty=2)
         side.insert(order) 
         self.assertEqual(1,side.get_order(order_id=4).price)
         self.assertEqual(4,side.get_order(order_id=4).order_id)
         self.assertEqual(4,side.get_num_orders())
         self.assertEqual(1,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(5,side.get_price_at_level(0))
         self.assertEqual(0,side.get_num_orders_at_level(1))
         self.assertEqual(4,side.get_price_at_level(1))
         self.assertEqual(1,side.get_num_orders_at_level(2))
         self.assertEqual(3,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(2,side.get_price_at_level(3))


         # test removal of deep order 
         side.delete(4)
 
         self.assertEqual(0,side.get_num_deep_orders())
         self.assertEqual(3,side.get_num_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(5,side.get_price_at_level(0))
         self.assertEqual(0,side.get_num_orders_at_level(1))
         self.assertEqual(4,side.get_price_at_level(1))
         self.assertEqual(1,side.get_num_orders_at_level(2))
         self.assertEqual(3,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(2,side.get_price_at_level(3))

         #test qty 
         self.assertEqual(1,side.get_qty_at_level(0))
         self.assertEqual(0,side.get_qty_at_level(1))
         self.assertEqual(1,side.get_qty_at_level(2))
         self.assertEqual(1,side.get_qty_at_level(3))


    def test_basic_ask(self):
         side=Side(is_ask=True,init_size=4,level_increment=1)
         order=Order(order_id=0,price=5,is_ask=True,qty=1)
         side.insert(order)
         self.assertEqual(5,side.get_order(order_id=0).price)
         self.assertEqual(0,side.get_order(order_id=0).order_id)
         self.assertEqual(5,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders()) 
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(5,side.get_price_at_level(0))

         order=Order(order_id=1,price=3,is_ask=True,qty=1)
         side.insert(order)
         self.assertEqual(3,side.get_order(order_id=1).price)
         self.assertEqual(1,side.get_order(order_id=1).order_id)
         self.assertEqual(3,side.get_price_at_level(0))
         self.assertEqual(2,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(3,side.get_price_at_level(0))
         self.assertEqual(0,side.get_num_orders_at_level(1))
         self.assertEqual(4,side.get_price_at_level(1))

         order=Order(order_id=2,price=2,is_ask=True,qty=1)
         side.insert(order)

         self.assertEqual(2,side.get_order(order_id=2).price)
         self.assertEqual(2,side.get_order(order_id=2).order_id)
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(3,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(3,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(5,side.get_price_at_level(3))


         order=Order(order_id=3,price=1,is_ask=True,qty=1)
         side.insert(order)
         self.assertEqual(1,side.get_order(order_id=3).price)
         self.assertEqual(3,side.get_order(order_id=3).order_id)
         self.assertEqual(1,side.get_price_at_level(0))
         self.assertEqual(4,side.get_num_orders())
         self.assertEqual(1,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(1,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(2,side.get_price_at_level(1))
         self.assertEqual(1,side.get_num_orders_at_level(2))
         self.assertEqual(3,side.get_price_at_level(2))
         self.assertEqual(0,side.get_num_orders_at_level(3))
         self.assertEqual(4,side.get_price_at_level(3))

         # test deletion from circ_array 
         side.delete(3)
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(3,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(1,side.get_num_orders_at_level(0))
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(3,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(5,side.get_price_at_level(3))

         order=Order(order_id=4,price=2,is_ask=True,qty=2)
         side.insert(order) 
         self.assertEqual(2,side.get_order(order_id=4).price)
         self.assertEqual(4,side.get_order(order_id=4).order_id)
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(4,side.get_num_orders())
         self.assertEqual(0,side.get_num_deep_orders())

         self.assertEqual(2,side.get_num_orders_at_level(0))
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(3,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(5,side.get_price_at_level(3))


         # test removal of deep order 
         order=Order(order_id=5,price=6,is_ask=True,qty=1)
         side.insert(order)
         self.assertEqual(6,side.get_order(order_id=5).price)
         self.assertEqual(5,side.get_order(order_id=5).order_id)
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(5,side.get_num_orders())
         self.assertEqual(1,side.get_num_deep_orders())

         self.assertEqual(2,side.get_num_orders_at_level(0))
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(3,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(5,side.get_price_at_level(3))

         side.delete(5)
 
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(0,side.get_num_deep_orders())
         self.assertEqual(4,side.get_num_orders())

         self.assertEqual(2,side.get_num_orders_at_level(0))
         self.assertEqual(2,side.get_price_at_level(0))
         self.assertEqual(1,side.get_num_orders_at_level(1))
         self.assertEqual(3,side.get_price_at_level(1))
         self.assertEqual(0,side.get_num_orders_at_level(2))
         self.assertEqual(4,side.get_price_at_level(2))
         self.assertEqual(1,side.get_num_orders_at_level(3))
         self.assertEqual(5,side.get_price_at_level(3))

         #test qty 
         self.assertEqual(3,side.get_qty_at_level(0))
         self.assertEqual(1,side.get_qty_at_level(1))
         self.assertEqual(0,side.get_qty_at_level(2))
         self.assertEqual(1,side.get_qty_at_level(3))

    def test_get_index_at_price(self):
         side=Side(is_ask=True,init_size=4,level_increment=1)
         order=Order(0,5,True)
         side.insert(order)
         self.assertEqual(side.top_index_price, 5)
         self.assertEqual(side.top_index, 2)
         self.assertEqual(3, side.get_index_at_price(6)) 
         self.assertEqual(1,side.get_index_at_price(8))
         self.assertEqual(None,side.get_index_at_price(9))
         self.assertEqual(1, side.get_index_at_price(4))
         self.assertEqual(0, side.get_index_at_price(3))
         self.assertEqual(3, side.get_index_at_price(2))
         self.assertEqual(None, side.get_index_at_price(1))

    def test_get_level_at_price(self):
         side=Side(is_ask=True,init_size=4,level_increment=1)
         order=Order(0,5,True)
         side.insert(order)
         self.assertEqual(side.top_index_price, 5)
         self.assertEqual(side.top_index, 2)
         self.assertEqual(1, side.get_level_at_price(6)) 
         self.assertEqual(3,side.get_level_at_price(8))
         self.assertEqual(4,side.get_level_at_price(9))
         self.assertEqual(0, side.get_level_at_price(5))
         self.assertEqual(-1, side.get_level_at_price(4))

         side=Side(is_ask=False,init_size=4,level_increment=1)
         order=Order(0,5,False)
         side.insert(order)
         self.assertEqual(side.top_index_price, 5)
         self.assertEqual(side.top_index, 2)
         self.assertEqual(-1,side.get_level_at_price(6)) 
         self.assertEqual(-3,side.get_level_at_price(8))
         self.assertEqual(-4,side.get_level_at_price(9))
         self.assertEqual(0, side.get_level_at_price(5))
         self.assertEqual(1, side.get_level_at_price(4))

    def test_deep_level_limit(self):
         side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
         order=Order(0,5,True)
         out=side.insert(order)
         self.assertEqual(out[0],True)
         order=Order(1,15,True)
         out=side.insert(order)
         self.assertEqual(out[0],False)

         side=Side(is_ask=False,init_size=4,level_increment=1,deep_level_limit=10)
         order=Order(0,20,False)
         out=side.insert(order)
         self.assertEqual(out[0],True)
         order=Order(1,10,False)
         out=side.insert(order)
         self.assertEqual(out[0],False)

    # test deletion from top of book, and make sure that the top sets it self correctly
    # when there is empty levels in between
    def test_delete_from_top_book(self):
        side=Side(is_ask=True,init_size=10,level_increment=1,deep_level_limit=10)
        order=Order(0,10,True)
        out=side.insert(order)
        self.assertEqual(out[0],True)

        order=Order(1,14,True)
        out=side.insert(order)
        self.assertEqual(out[0],True)

        side.delete(0)
        self.assertEqual(out[0],True)
        self.assertEqual(side.get_price_at_level(0),14)

        side=Side(is_ask=False,init_size=10,level_increment=1,deep_level_limit=10)
        order=Order(0,8,False)
        out=side.insert(order)
        self.assertEqual(out[0],True)

        order=Order(1,10,False)
        out=side.insert(order)
        self.assertEqual(out[0],True)

        side.delete(1)
        self.assertEqual(out[0],True)
        self.assertEqual(side.get_price_at_level(0),8)

    
    # test deletion from top of book, and make sure that the top sets it self correctly
    # when the only other order is deep in book
    def test_delete_from_top_book(self):
        side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(0,10,True)
        out=side.insert(order)
        self.assertEqual(out[0],True)

        order=Order(1,18,True)
        out=side.insert(order)
        self.assertEqual(out[0],True)
        self.assertEqual(side.get_num_deep_orders(),1)

        side.delete(0)
        self.assertEqual(out[0],True)
        self.assertEqual(side.get_price_at_level(0),18)
        self.assertEqual(side.get_num_deep_orders(),0)

        side=Side(is_ask=False,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(0,2,False)
        out=side.insert(order)
        self.assertEqual(out[0],True)

        order=Order(1,10,False)
        out=side.insert(order)
        self.assertEqual(out[0],True)
        self.assertEqual(side.get_num_deep_orders(),1)

        side.delete(1)
        self.assertEqual(out[0],True)
        self.assertEqual(side.get_price_at_level(0),2)
        self.assertEqual(side.get_num_deep_orders(),0)

    # test matching of Side class
    def test_matching(self):
        # test taking one full and one partial orders in book
        side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(order_id=0,price=3,is_ask=True,qty=1,creation_time=1)
        side.insert(order)
            
        order=Order(order_id=1,price=4,is_ask=True,qty=2,creation_time=1)
        side.insert(order)

        order=Order(order_id=2,price=5,is_ask=False,qty=2,creation_time=2)
        matching=side.get_matching_orders(order)
        
        self.assertEqual(len(matching),2)        
        self.assertEqual(matching[0][0],0)
        self.assertEqual(matching[0][1],1)
        self.assertEqual(matching[0][2],1)
 
        self.assertEqual(matching[1][0],1)
        self.assertEqual(matching[1][1],2)
        self.assertEqual(matching[1][2],1)

        # now test for bid side
        side=Side(is_ask=False,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(order_id=0,price=3,is_ask=False,qty=2,creation_time=1)
        side.insert(order)
            
        order=Order(order_id=1,price=4,is_ask=False,qty=1,creation_time=1)
        side.insert(order)

        order=Order(order_id=2,price=3,is_ask=True,qty=2,creation_time=2)
        matching=side.get_matching_orders(order)
        
        self.assertEqual(len(matching),2)        
        self.assertEqual(matching[0][0],1)
        self.assertEqual(matching[0][1],1)
        self.assertEqual(matching[0][2],1)
 
        self.assertEqual(matching[1][0],0)
        self.assertEqual(matching[1][1],2)
        self.assertEqual(matching[1][2],1)


        # test taking of one out of two orders in book
        side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(order_id=0,price=3,is_ask=True,qty=1,creation_time=1)
        side.insert(order)
            
        order=Order(order_id=1,price=5,is_ask=True,qty=2,creation_time=1)
        side.insert(order)

        order=Order(order_id=2,price=4,is_ask=False,qty=2,creation_time=2)

        matching=side.get_matching_orders(order)

        self.assertEqual(len(matching),1)        
        self.assertEqual(matching[0][0],0)
        self.assertEqual(matching[0][1],1)
        self.assertEqual(matching[0][2],1)


        # now test for bid side
        side=Side(is_ask=False,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(order_id=0,price=3,is_ask=False,qty=2,creation_time=1)
        side.insert(order)
            
        order=Order(order_id=1,price=1,is_ask=False,qty=2,creation_time=1)
        side.insert(order)

        order=Order(order_id=2,price=2,is_ask=True,qty=2,creation_time=2)

        matching=side.get_matching_orders(order)

        self.assertEqual(len(matching),1)        
        self.assertEqual(matching[0][0],0)
        self.assertEqual(matching[0][1],2)
        self.assertEqual(matching[0][2],2)


    # test to see if deep orders get matched
    def test_deep_matching(self):
        side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(order_id=0,price=3,is_ask=True,qty=1,creation_time=1)
        side.insert(order)
            
        order=Order(order_id=1,price=12,is_ask=True,qty=2,creation_time=1)
        side.insert(order)

        order=Order(order_id=2,price=5,is_ask=False,qty=2,creation_time=2)
        matching=side.get_matching_orders(order)
        
        self.assertEqual(len(matching),2)        
        self.assertEqual(matching[0][0],0)
        self.assertEqual(matching[0][1],1)
        self.assertEqual(matching[0][2],1)
 
        self.assertEqual(matching[1][0],1)
        self.assertEqual(matching[1][1],2)
        self.assertEqual(matching[1][2],1)

    # test that level increment for price is enforced 
    def test_level_increment_reject(self):
        side=Side(is_ask=True,init_size=4,level_increment=2,deep_level_limit=10)
        order=Order(0,3,True)
        out=side.insert(order)
        self.assertEqual(out[0],False)

        side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(0,1.3,True)
        out=side.insert(order)
        self.assertEqual(out[0],False)

    # test to see if matching priority is respected
    def test_matching_priority(self):
        side=Side(is_ask=True,init_size=4,level_increment=1,deep_level_limit=10)
        order=Order(order_id=11,price=3,is_ask=True,qty=1,creation_time=1)
        side.insert(order)
            
        order=Order(order_id=1,price=3,is_ask=True,qty=1,creation_time=2)
        side.insert(order)

        order=Order(order_id=4,price=4,is_ask=True,qty=1,creation_time=3)
        side.insert(order)

        order=Order(order_id=101,price=3,is_ask=True,qty=1,creation_time=4)
        side.insert(order)

        order=Order(order_id=4,price=3,is_ask=True,qty=1,creation_time=5)
        side.insert(order)
        
        order=Order(order_id=2,price=3,is_ask=False,qty=3,creation_time=6)
        matching=side.get_matching_orders(order)
        self.assertEqual(len(matching),3)
        self.assertEqual(matching[0][0], 11)
        self.assertEqual(matching[1][0], 1)
        self.assertEqual(matching[2][0], 101)

    # test the existence of an order that gets moved around levels
    # TODO:
    def test_order_move(self):
        side=Side(is_ask=True,init_size=10,level_increment=1)
        order=Order(order_id=0,price=11,is_ask=True,qty=1)
        side.insert(order)
            
        order=Order(order_id=1,price=9,is_ask=True,qty=2)
        side.insert(order)

        order=Order(order_id=2,price=7,is_ask=True,qty=2)
        side.insert(order)

        side.delete(2)

        order=Order(order_id=3,price=25,is_ask=True,qty=2)
        
        side.delete(3)
        side.delete(1)
        side.delete(0)




if __name__ == '__main__':

    unittest.main()
