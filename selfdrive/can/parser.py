import time
from collections import defaultdict
import numbers

from selfdrive.can.libdbc_py import libdbc, ffi

class CANParser(object):
  def __init__(self, dbc_name, signals, checks=[], bus=0, sendcan=False):
    print '\n> ***** CANParser(object).__init__(dbc_name, signals, checks) START ***** [selfdrive/can/parser.py]' #JP
    print '  > [CANParser.__init__()] dbc_name = ', dbc_name #JP
    #print '   signals = \n', signals #JP
    print '  > [CANParser.__init__()] signals = ...' #JP
    #print '   checks = \n', checks #JP
    print '  > [CANParser.__init__()] checks = ...' #JP
    
    self.can_valid = True
    self.vl = defaultdict(dict)
    self.ts = defaultdict(dict)

    print '  > [CANParser.__init__()] call libdbc.dbc_lookup(dbc_name)' #JP
    self.dbc = libdbc.dbc_lookup(dbc_name)
    print '  > [CANParser.__init__()] dbc = ', self.dbc #JP
    self.msg_name_to_addres = {}
    self.address_to_msg_name = {}

    num_msgs = self.dbc[0].num_msgs
    print '  > [CANParser.__init__()] num_msgs = ', num_msgs #JP
    for i in range(num_msgs):
      msg = self.dbc[0].msgs[i]

      name = ffi.string(msg.name)
      address = msg.address
      print '   > [CANParser.__init__()] message Id = ', address, '   message name = ', name #JP
      print '   > [CANParser.__init__()] msg = ', msg #JP

      self.msg_name_to_addres[name] = address
      self.address_to_msg_name[address] = name
      #print 'self.msg_name_to_address[',name,'] = ', address #JP
      
    print '  > [CANParser.__init__()] name to address dictionary ...' #JP
    #print '   ', self.msg_name_to_addres, '\n' #JP
    print '  > [CANParser.__init__()] address to name dictionary ...' #JP
    #print '   ', self.address_to_msg_name, '\n' #JP

    # Convert message names into adresses
    print '  > [CANParser.__init__()] # Convert message names into addresses (openpilot comment)' #JP
    for i in range(len(signals)):
      s = signals[i]
      #print '   s = ', s #JP
      #print '   s[0] = ', s[0] #JP
      #print '   s[1] = ', s[1] #JP
      #print '   s[2] = ', s[2] #JP
      if not isinstance(s[1], numbers.Number):
        s = (s[0], self.msg_name_to_addres[s[1]], s[2])
        signals[i] = s
        #print 'signals[',i,'] = ', s #JP

    for i in range(len(checks)):
      c = checks[i]
      if not isinstance(c[0], numbers.Number):
        c = (self.msg_name_to_addres[c[0]], c[1])
        checks[i] = c
    #print '> selfdrive/can/parser.py CANParser(object).__init__() checks = ', checks #JP

    sig_names = dict((name, ffi.new("char[]", name)) for name, _, _ in signals)

    # Set default values by name
    print '  > [CANParser.__init__()] # set default values by name (openpilot comment)' #JP
    for sig_name, sig_address, sig_default in signals:
      self.vl[self.address_to_msg_name[sig_address]][sig_name] = sig_default

    signal_options_c = ffi.new("SignalParseOptions[]", [
      {
        'address': sig_address,
        'name': sig_names[sig_name],
        'default_value': sig_default,
      } for sig_name, sig_address, sig_default in signals])

    message_options = dict((address, 0) for _, address, _ in signals)
    #print '> selfdrive/can/parser.py CANParser(object).__init__() message_options before checks =',message_options #JP
    message_options.update(dict(checks))

    message_options_c = ffi.new("MessageParseOptions[]", [
      {
        'address': msg_address,
        'check_frequency': freq,
      } for msg_address, freq in message_options.iteritems()])
    #print '> selfdrive/can/parser.py CANParser(object).__init__() message_options_c = ', message_options_c #JP

    print '  > [CANParser.__init__()] call self.can = libdbc.can_init(bus, dbc_name, ..., sendcan)' #JP
    self.can = libdbc.can_init(bus, dbc_name, len(message_options_c), message_options_c,
                               len(signal_options_c), signal_options_c, sendcan)
    print '  > [CANParser.__init__()] self.can = ', self.can #JP
    self.p_can_valid = ffi.new("bool*")

    value_count = libdbc.can_query(self.can, 0, self.p_can_valid, 0, ffi.NULL)
    self.can_values = ffi.new("SignalValue[%d]" % value_count)
    print '   > [CANParser.__init__()] call self.can_values = ffi.new(\"SignalValue[%d]\" % value_count)' #JP
    print '   > [CANParser.__init__()] call self.update_vl()' #JP
    self.update_vl(0)
    # print "==="

  def update_vl(self, sec):
    print '\n> ***** CANParser.update_vl(sec) START ***** return ret [selfdrive/can/parser.py]' #JP 

    can_values_len = libdbc.can_query(self.can, sec, self.p_can_valid, len(self.can_values), self.can_values)
    assert can_values_len <= len(self.can_values)

    self.can_valid = self.p_can_valid[0]

    # print can_values_len
    ret = set()
    for i in xrange(can_values_len):
      cv = self.can_values[i]
      address = cv.address
      # print hex(cv.address), ffi.string(cv.name)
      name = ffi.string(cv.name)
      self.vl[address][name] = cv.value
      self.ts[address][name] = cv.ts

      sig_name = self.address_to_msg_name[address]
      self.vl[sig_name][name] = cv.value
      self.ts[sig_name][name] = cv.ts
      ret.add(address)
    print '  > [CANParser.update_vl()] type(ret) = ', type(ret) #JP  
    print '> ***** CANParser.update_vl() END ***** return ret [parser.py CANParser()]\n' #JP  
    return ret

  def update(self, sec, wait):
    print '\n> ***** CANParser.update() START ***** return self.update_vl() [parser.py]' #JP  
    print '  > [CANParser.update()] call libdbc.can_update(self.can, ...)' #JP  
    print '    > libdbc.can_update() uses functions is parser.cc; libdbc.can_update() is declared in libdbc_py.py' #JP  
    libdbc.can_update(self.can, sec, wait)
    print '\n> ***** CANParser.update() END ***** return self.update_vl() [parser.py]' #JP  
    return self.update_vl(sec)

if __name__ == "__main__":
  from common.realtime import sec_since_boot

  radar_messages = range(0x430, 0x43A) + range(0x440, 0x446)
  # signals = zip(['LONG_DIST'] * 16 + ['NEW_TRACK'] * 16 + ['LAT_DIST'] * 16 +
  #               ['REL_SPEED'] * 16, radar_messages * 4,
  #               [255] * 16 + [1] * 16 + [0] * 16 + [0] * 16)
  # checks = zip(radar_messages, [20]*16)

  # cp = CANParser("acura_ilx_2016_nidec", signals, checks, 1)


  # signals = [
  #   ("XMISSION_SPEED", 0x158, 0), #sig_name, sig_address, default
  #   ("WHEEL_SPEED_FL", 0x1d0, 0),
  #   ("WHEEL_SPEED_FR", 0x1d0, 0),
  #   ("WHEEL_SPEED_RL", 0x1d0, 0),
  #   ("STEER_ANGLE", 0x14a, 0),
  #   ("STEER_TORQUE_SENSOR", 0x18f, 0),
  #   ("GEAR", 0x191, 0),
  #   ("WHEELS_MOVING", 0x1b0, 1),
  #   ("DOOR_OPEN_FL", 0x405, 1),
  #   ("DOOR_OPEN_FR", 0x405, 1),
  #   ("DOOR_OPEN_RL", 0x405, 1),
  #   ("DOOR_OPEN_RR", 0x405, 1),
  #   ("CRUISE_SPEED_PCM", 0x324, 0),
  #   ("SEATBELT_DRIVER_LAMP", 0x305, 1),
  #   ("SEATBELT_DRIVER_LATCHED", 0x305, 0),
  #   ("BRAKE_PRESSED", 0x17c, 0),
  #   ("CAR_GAS", 0x130, 0),
  #   ("CRUISE_BUTTONS", 0x296, 0),
  #   ("ESP_DISABLED", 0x1a4, 1),
  #   ("HUD_LEAD", 0x30c, 0),
  #   ("USER_BRAKE", 0x1a4, 0),
  #   ("STEER_STATUS", 0x18f, 5),
  #   ("WHEEL_SPEED_RR", 0x1d0, 0),
  #   ("BRAKE_ERROR_1", 0x1b0, 1),
  #   ("BRAKE_ERROR_2", 0x1b0, 1),
  #   ("GEAR_SHIFTER", 0x191, 0),
  #   ("MAIN_ON", 0x326, 0),
  #   ("ACC_STATUS", 0x17c, 0),
  #   ("PEDAL_GAS", 0x17c, 0),
  #   ("CRUISE_SETTING", 0x296, 0),
  #   ("LEFT_BLINKER", 0x326, 0),
  #   ("RIGHT_BLINKER", 0x326, 0),
  #   ("COUNTER", 0x324, 0),
  #   ("ENGINE_RPM", 0x17C, 0)
  # ]
  # checks = [
  #   (0x14a, 100), # address, frequency
  #   (0x158, 100),
  #   (0x17c, 100),
  #   (0x191, 100),
  #   (0x1a4, 50),
  #   (0x326, 10),
  #   (0x1b0, 50),
  #   (0x1d0, 50),
  #   (0x305, 10),
  #   (0x324, 10),
  #   (0x405, 3),
  # ]

  # cp = CANParser("honda_civic_touring_2016_can_generated", signals, checks, 0)


  signals = [
    # sig_name, sig_address, default
    ("GEAR", 956, 0x20),
    ("BRAKE_PRESSED", 548, 0),
    ("GAS_PEDAL", 705, 0),

    ("WHEEL_SPEED_FL", 170, 0),
    ("WHEEL_SPEED_FR", 170, 0),
    ("WHEEL_SPEED_RL", 170, 0),
    ("WHEEL_SPEED_RR", 170, 0),
    ("DOOR_OPEN_FL", 1568, 1),
    ("DOOR_OPEN_FR", 1568, 1),
    ("DOOR_OPEN_RL", 1568, 1),
    ("DOOR_OPEN_RR", 1568, 1),
    ("SEATBELT_DRIVER_UNLATCHED", 1568, 1),
    ("TC_DISABLED", 951, 1),
    ("STEER_ANGLE", 37, 0),
    ("STEER_FRACTION", 37, 0),
    ("STEER_RATE", 37, 0),
    ("GAS_RELEASED", 466, 0),
    ("CRUISE_STATE", 466, 0),
    ("MAIN_ON", 467, 0),
    ("SET_SPEED", 467, 0),
    ("STEER_TORQUE_DRIVER", 608, 0),
    ("STEER_TORQUE_EPS", 608, 0),
    ("TURN_SIGNALS", 1556, 3),   # 3 is no blinkers
    ("LKA_STATE", 610, 0),
  ]
  checks = [
    (548, 40),
    (705, 33),

    (170, 80),
    (37, 80),
    (466, 33),
    (608, 50),
  ]

  cp = CANParser("toyota_rav4_2017_pt_generated", signals, checks, 0)

  # print cp.vl

  while True:
    cp.update(int(sec_since_boot()*1e9), True)
    # print cp.vl
    print cp.ts
    print cp.can_valid
    time.sleep(0.01)
