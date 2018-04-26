import zmq

from cereal import log
from common import realtime

def new_message():
  dat = log.Event.new_message()
  dat.logMonoTime = int(realtime.sec_since_boot() * 1e9)
  return dat

def pub_sock(context, port, addr="*"):
  sock = context.socket(zmq.PUB)
  sock.bind("tcp://%s:%d" % (addr, port))
  return sock

def sub_sock(context, port, poller=None, addr="127.0.0.1", conflate=False):
  sock = context.socket(zmq.SUB)
  if conflate:
    sock.setsockopt(zmq.CONFLATE, 1)
  sock.connect("tcp://%s:%d" % (addr, port))
  sock.setsockopt(zmq.SUBSCRIBE, "")
  if poller is not None:
    poller.register(sock, zmq.POLLIN)
  return sock

def drain_sock(sock, wait_for_one=False):
  print '      > selfdrive/messaging.py drain_sock(sock)' #JP
  # print '  wait_for_one = ', wait_for_one #JP
  ret = []
  print '      > selfdrive/messaging.py drain_sock(sock) wait_for_one = ', wait_for_one #JP
  while 1:
    try:
      if wait_for_one and len(ret) == 0:
        dat = sock.recv()
        print '      > selfdrive/messaging.py drain_sock(sock) first if dat = ', dat #JP
      else:
        print '      > selfdrive/messaging.py drain_sock() call dat = sock.recv(zmq.NOBLOCK)' #JP
        dat = sock.recv(zmq.NOBLOCK) 
        #dat = sock.recv() #JP added
        print 'hello world!' #JP
      dat = log.Event.from_bytes(dat) #JP commented out
      print '      > selfdrive/messaging.py drain_sock() type(dat) = ', type(dat) #JP
      ret.append(dat)
    except zmq.error.Again:
      break
  print '      > selfdrive/messaging.py drain_sock() returns ret = ',ret    
  return ret


# TODO: print when we drop packets?
def recv_sock(sock, wait=False):
  print '  > [selfdrive/messaging.py] recv_sock() sock = ', sock.getsockopt(zmq.FD) #JP
  # print '  > sock = ', sock #JP
  dat = None
  while 1:
    try:
      if wait and dat is None:
        print 'wait = ', wait
        print 'dat = ', dat
        print '[if wait and dat is None] dat = sock.recv()' #JP
        dat = sock.recv()
      else:
        dat = sock.recv(zmq.NOBLOCK)
        print 'zmq.NOBLOCK' #JP
    except zmq.error.Again:
      print '> [recv_sock()] ***** zmq.error.Again *****' #JP
      break
  if dat is not None:
    dat = log.Event.from_bytes(dat) #JP commented out for zmq test
    #print '  selfdrive/messaging.py recv_sock()' #JP
    print '> [recv_sock() if dat is not None]     dat = ', dat #JP
  print '     > recv_sock() return dat [messaging.py]' #JP
  return dat

def recv_one(sock):
  return log.Event.from_bytes(sock.recv())

def recv_one_or_none(sock):
  try:
    return log.Event.from_bytes(sock.recv(zmq.NOBLOCK))
  except zmq.error.Again:
    return None
