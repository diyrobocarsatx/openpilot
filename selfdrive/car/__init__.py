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

  TOYOTA.PRIUS: ToyotaInterface,
  TOYOTA.RAV4: ToyotaInterface,
  TOYOTA.RAV4H: ToyotaInterface,
  TOYOTA.COROLLA: ToyotaInterface,
  TOYOTA.LEXUS_RXH: ToyotaInterface,
  #TOYOTA.KIA: ToyotaInterface, #JP

  "simulator2": Sim2Interface,
  "mock": MockInterface
}

# **** for use live only ****
def fingerprint(logcan, timeout):
  print '  > [car.py __init__.py] fingerprint(logcan, timeout) START ***** return candidate_cars[0], finger' #JP

  print '  > [fingerprint()] call candidate_cars = all_known_cars()' #JP
  candidate_cars = all_known_cars()
  if os.getenv("SIMULATOR2") is not None:
    return ("simulator2", None)

  finger_st = sec_since_boot()

  cloudlog.warning("     [fingerprint()]    waiting for fingerprint...\n")
  finger = {}
  st = None
  print '    > [fingerprint()] st = ', st #JP 
  myCounter = 1 #JP
  while 1:
    print '\n   > [fingerprint()] while 1 loop START ***' #JP
    if (myCounter%5 == 0): #JP
      print '    > counter = ', myCounter #JP
    myCounter += 1 #JP
    print '    > [fingerprint()]  call messaging.drain_sock(logcan, ...)' #JP
    #for a in messaging.drain_sock(logcan, wait_for_one=True): #JP commented out
    for a in messaging.drain_sock(logcan, wait_for_one=False): #JP
      print '>>> inside for a in messaging.drain_sock loop' #JP

      if st is None:
        st = sec_since_boot()
      for can in a.can:
#        cloudlog.info('\n>>> inside for can in a.can loop') #JP
#        cloudlog.info('>>> a.can is: ' + str(a.can)) #JP
        if can.src == 0:
#          cloudlog.info('>>> can.src = 0') #JP
          finger[can.address] = len(can.dat)
        candidate_cars = eliminate_incompatible_cars(can, candidate_cars)

    st = sec_since_boot() #JP added so that st is not None
    ts = sec_since_boot()
    print '    > [fingerprint()] ts = ', ts #JP 

    # exit if there is only one car choice and time_fingerprint since
    # the first message has elapsed. Toyota needs higher
    # time_fingerprint, since DSU does not broadcast immediately
    print '    > [fingerprint()] len(candidate_cars) = ', len(candidate_cars) #JP 
    print '    > [fingerprint()] st = ', st #JP 
    print '    > [fingerprint()] timeout = ', timeout #JP 
    print '    > [fingerprint()] finger_st = ', finger_st #JP 
    myBoolean = timeout and ts-finger_st > timeout #JP
    print '    > [fingerprint()] (timeout and ts-finger_st > timeout) = ', myBoolean #JP
    if len(candidate_cars) == 1 and st is not None:
      # TODO: better way to decide to wait more if Toyota
      time_fingerprint = 1.0 if ("TOYOTA" in candidate_cars[0] or "LEXUS" in candidate_cars[0]) else 0.1
      if (ts-st) > time_fingerprint:
        break

    # bail if no cars left or we've been waiting too long
    elif len(candidate_cars) == 0 or (timeout and ts-finger_st > timeout):
      #cloudlog.info('the length of candidate_cars =' + len(candidate_car)) #JP
      return None, finger
    print '  > [fingerprint()] while 1 loop END ***' #JP  
    if myCounter == 2: break #JP 
  print '\n  > [fingerprint()] fingerprinted = ', candidate_cars[0] #JP
  print '  > [fingerprint()] finger = ', finger, '\n' #JP
  print '  > fingerprint() END *** car/__init__.py\n' #JP
  #return (candidate_cars[0], finger)
  return ('KIA SOUL 2016', finger)


def get_car(logcan, sendcan=None, passive=True):
  # TODO: timeout only useful for replays so controlsd can start before unlogger
  print '\n  > [__init__.py] get_car(logcan, sendcan) START **** return interface_cls(params, sendcan), params selfdrive/car' #JP
  print '\n  > [get_car()] call candidate, fingerprint = fingerprint(logcan, timeout)' #JP
  timeout = 1. if passive else None
  print '> [get_car()] timeout = ', timeout #JP
  print '> [get_car()] passive = ', passive #JP
  #candidate, fingerprints = fingerprint(logcan, timeout)
  candidate = 'TOYOTA COROLLA 2017' #JP
  fingerprints = {36: 8, 37: 8, 170: 8, 180: 8, 186: 4, 426: 6, 452: 8, 464: 8, 466: 8, 467: 8, 547: 8, 548: 8, 552: 4, 608: 8, 610: 5, 643: 7, 705: 8, 740: 5, 800: 8, 835: 8, 836: 8, 849: 4, 869: 7, 870: 7, 871: 2, 896: 8, 897: 8, 900:6, 902: 6, 905: 8, 911: 8, 916: 2, 921: 8, 933: 8, 944: 8, 945: 8, 951: 8, 955: 4, 956: 8, 979: 2, 992: 8, 998: 5, 999: 7, 1000: 8, 1001: 8, 1017: 8, 1041: 8, 1042: 8, 1043: 8, 1044: 8, 1056: 8, 1059: 1, 1114: 8, 1161: 8, 1162: 8, 1163: 8, 1196: 8, 1227: 8, 1235: 8, 1279: 8, 1552: 8, 1553: 8, 1556: 8, 1557: 8, 1561: 8, 1562: 8, 1568: 8, 1569: 8, 1570: 8, 1571: 8, 1572: 8, 1584: 8, 1589: 8, 1592: 8, 1596: 8, 1597: 8, 1600: 8, 1664: 8, 1728: 8, 1779: 8, 1904: 8, 1912: 8, 1990: 8, 1998: 8}

 # fingerprints = {112L: 8, 113L: 8, 114L: 8, 115L: 8, 128L: 8, 129L: 8, 130L: 8, 131L: 8, 144L: 8, 145L: 8, 146L: 8, 147L: 8, 175L:8} #JP KIA
  if candidate is None:
    cloudlog.warning("car doesn't match any fingerprints: %r", fingerprints)
    if passive:
      candidate = "mock"
    else:
      return None, None

  interface_cls = interfaces[candidate]
  print '  > [get_car()] candidate = ', candidate #JP
  print '  > [get_car()] interface_cls = ',interface_cls #JP
  print '  > [get_car()] fingerprints = ', fingerprints #JP
  print '  > [get_car()] call params = interface_cls.get_params(candidate, fingerprints)' #JP
  params = interface_cls.get_params(candidate, fingerprints)
  # print '  > selfdrive/car/__init__.py get_car() params = interface_cls.get_params(candidate, fingerprints)', params #JP

  print '> [get_car()]  call return interface_class(params, sendcan) and END *****' #JP
  return interface_cls(params, sendcan), params
