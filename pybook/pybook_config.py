# Contains configurations for running pybook_client and pybook_server
# note that pybook_server/client has to be both restarted for changes
# to take place


# first currency in the tuple is the instrument, second currency is the unit
#
CONFIG_DICT={
    # level_increment == price_increment
    #
    # note that in order to gurantee non decimal qty 
    # level_increment * (min_qty+X*qty_increment) must be equal to the base units per nominal of the instrument
    #
    #
    ('LTC','BTC'):{
        'port'              :5006,
        'level_increment'   :1000,       # .00001 BTC
        'init_size'         :500,
        'qty_increment'     :100000,   # .001 LTC
        'min_qty'           :100000,   # .001 LTC 
        'max_qty'           :100000000, # 1 LTC
        'min_price'         :100000,    # .001 BTC
        'max_price'         :100000000, # 1 BTC
        'deep_level_limit'  :None},    

    ('DOGE','BTC'):{
        'port'              :5005,
        'level_increment'   :1,
        'init_size'         :500,
        'qty_increment'     :100000000, # 1 DOGE
        'min_qty'           :100000000,
        'max_qty'           :10000000000, #100 DOGE
        'min_price'         :1,
        'max_price'         :200,
        'deep_level_limit'  :None},

    # these are test coins , for testing the exchange 
    ('LTC_TESTNET','BTC_TESTNET'):{
        'port'              :5004,
        'level_increment'   :100,       # .000001 BTC
        'init_size'         :500,
        'qty_increment'     :1000000,   # .01 LTC
        'min_qty'           :1000000,   # .01 LTC 
        'max_qty'           :100000000, # 1 LTC
        'min_price'         :100000,    # .001 BTC
        'max_price'         :100000000, # 1 BTC
        'deep_level_limit'  :None}, 
 
    }

BUFFER_SIZE=1024
TCP_IP='127.0.0.1'
