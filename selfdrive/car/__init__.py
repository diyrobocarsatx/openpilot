import os

from common.realtime import sec_since_boot
from common.fingerprints import eliminate_incompatible_cars, all_known_cars

from selfdrive.swaglog import cloudlog
import selfdrive.messaging as messaging
from selfdrive.car.honda.interface import CarInterface as HondaInterface
from selfdrive.car.toyota.interface import CarInterface as ToyotaInterface
from selfdrive.car.mock.interface import CarInterface as MockInterface
from common.fingerprints import HONDA, TOYOTA

try:
  from .simulator.interface import CarInterface as SimInterface
except ImportError:
  SimInterface = None

try:
  from .simulator2.interface import CarInterface as Sim2Interface
except ImportError:
  Sim2Interface = None


interfaces = {
  HONDA.CIVIC: HondaInterface,
  HONDA.ACURA_ILX: HondaInterface,
  HONDA.CRV: HondaInterface,
  HONDA.ODYSSEY: HondaInterface,
  HONDA.ACURA_RDX: HondaInterface,  
  HONDA.PILOT: HondaInterface,
  HONDA.KIA: HondaInterface, #JP

  TOYOTA.PRIUS: ToyotaInterface,
  TOYOTA.RAV4: ToyotaInterface,
  TOYOTA.RAV4H: ToyotaInterface,
  TOYOTA.COROLLA: ToyotaInterface,
  TOYOTA.LEXUS_RXH: ToyotaInterface,

  "simulator2": Sim2Interface,
  "mock": MockInterface
}

# **** for use live only ****
def fingerprint(logcan, timeout):
  print '  > selfdrive/car/__init__.py fingerprint(logcan)' #JP

  candidate_cars = all_known_cars()
  if os.getenv("SIMULATOR2") is not None:
    return ("simulator2", None)

  finger_st = sec_since_boot()

  cloudlog.warning("   waiting for fingerprint...\n")
  finger = {}
  st = None
  myCounter = 0 #JP
  while 1:
    if (myCounter%1 == 0): #JP
      print '\n   selfdrive/car/__init__.py fingerprint(): while 1 loop' #JP

      print '    counter = ', myCounter #JP
      #cloudlog.info('time since boot =' + str(ts)) #JP
    myCounter += 1 #JP
    #for a in messaging.drain_sock(logcan, wait_for_one=True): #JP commented out
    for a in messaging.drain_sock(logcan, wait_for_one=False): #JP
      print '>>> inside for a in messaging.drain_sock loop' #JP

      if st is None:
        cloudlog.info('>>> st = ' + str(st)) #JP
        st = sec_since_boot()
      for can in a.can:
#        cloudlog.info('\n>>> inside for can in a.can loop') #JP
#        cloudlog.info('>>> a.can is: ' + str(a.can)) #JP
        if can.src == 0:
#          cloudlog.info('>>> can.src = 0') #JP
          finger[can.address] = len(can.dat)
        candidate_cars = eliminate_incompatible_cars(can, candidate_cars)
#     with open('mgrTT', 'a+') as f: #JP
#         f.write('\n candidate cars = '+ str(candidate_cars)) #JP

    ts = sec_since_boot()

    # exit if there is only one car choice and time_fingerprint since
    # the first message has elapsed. Toyota needs higher
    # time_fingerprint, since DSU does not broadcast immediately
    if len(candidate_cars) == 1 and st is not None:
      # TODO: better way to decide to wait more if Toyota
      time_fingerprint = 1.0 if ("TOYOTA" in candidate_cars[0] or "LEXUS" in candidate_cars[0]) else 0.1
      if (ts-st) > time_fingerprint:
        break

    # bail if no cars left or we've been waiting too long
    elif len(candidate_cars) == 0 or (timeout and ts-finger_st > timeout):
      cloudlog.info('the length of candidate_cars =' + len(candidate_car)) #JP
      return None, finger
    if myCounter == 2: break #JP 
  #cloudlog.warning("fingerprinted %s", candidate_cars[0]) #JP commented
  print '\n ***  fingerprinted = ', candidate_cars[0] #JPj
  print '    > selfdrive/car/__init__.py fingerprint() return candidate_cars[0], finger\n' #JP
  return (candidate_cars[0], finger)


def get_car(logcan, sendcan=None, passive=True):
  # TODO: timeout only useful for replays so controlsd can start before unlogger
  print '\n  > selfdrive/car/__init__.py get_car(logcan) return interface_cls(params, sendcan), params' #JP
  print '\n  > selfdrive/car/__init__.py get_car(logcan) call fingerprint(logcan)' #JP
  timeout = 1. if passive else None
  candidate, fingerprints = fingerprint(logcan, timeout)

  if candidate is None:
    cloudlog.warning("car doesn't match any fingerprints: %r", fingerprints)
    if passive:
      candidate = "mock"
    else:
      return None, None

  interface_cls = interfaces[candidate]
  print '  > selfdrive/car/__init__.py get_car() candidate = ', candidate #JP
  print '  > selfdrive/car/__init__.py get_car() interface_cls = ',interface_cls #JP
  print '  > selfdrive/car/__init__.py get_car() fingerprints = ', fingerprints #JP
  params = interface_cls.get_params(candidate, fingerprints)
  print '  > selfdrive/car/__init__.py get_car() params = interface_cls.get_params(candidate, fingerprints)' #JP
  # print '  > selfdrive/car/__init__.py get_car() params = interface_cls.get_params(candidate, fingerprints)', params #JP

  print '  > selfdrive/car/__init__.py get_car() call interface_class(params, sendcan)' #JP
  return interface_cls(params, sendcan), params
