from pybook import *
import pybook_config
from multiprocessing import Process
import SocketServer
import sys
sys.path.append('../')
from cryptoutils import socketmsg

BUFFER_SIZE=1024
TCP_IP='127.0.0.1'

def launch_instance(instrument,unit,port):

    book = Book.from_pybook_config(instrument,unit)

    server=SocketServer.TCPServer((TCP_IP,port),Handler)
    server.book=book
    server.serve_forever()
    
class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        while 1:
            msg=socketmsg.socketrecv(self.request,BUFFER_SIZE)
            if msg == None:
                return 
            out=self.server.book.process_msg(msg)
            socketmsg.socketsend(self.request,out) 
           

def getint_and_convert_none(config,section,var):
    out=config.get(section,var)
    if out.lower() == 'none':
        return None
    else:
        return int(out)


if __name__=='__main__':


    for pair in pybook_config.CONFIG_DICT: 
        instrument=pair[0]
        unit=pair[1]        
        port                = pybook_config.CONFIG_DICT[pair]['port']
        p=Process(target=launch_instance,args=(instrument,unit,port))
        p.start()

    p.join()

