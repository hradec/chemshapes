

import serial, time
import RepRapArduinoSerialSender

# M119 - read optos
# M114 - read positions XYZE
# M115 - print firmware info
# G1   - movement
# G92  - movement
# G28  - home all axis
# M201 - adjust accelaration ?!?
# M202 - adjust travel accelaration ?!?
# M92  - adjust speed?!
# M106 - Fan On (we can use to turn the tilt DC on)
# M107 - Fan On (we can use to turn the tilt DC off)
# M109 - Wait for extruder heater to reach target.
# M190 - Wait bed for heater to reach target.
# M104 - Set Extruder temp
# M140 - set bed temp


# M300 - home Z to bottom opto (evaluate middle - if open, slow mode)
# M301 - home Z to middle opto ( refill procedure!? )
# M302 - home Z to middle then to bottom opto (evaluate middle - if open, mode slow)
# M303 - home Z to middle then to bottom and return distance. 
# M320 - set steps per mm
# M321 - get steps per mm
# M330 - tilt vat



class axis():
    def __init__(self, axisName, device):
        self.device = device
        self._speed = 100
        self.name = axisName
        
    def speed( self, mmPerSec ):
        self._speed = mmPerSec 
        
    def move(self, mm, relative=False):
        if relative:
            self.device.write('G91')
        self.device.write('G1 %s%f F%f' % (self.name.upper(), mm, self._speed*16) )
        if relative:
            self.device.write('G90')
    

class device():
    def __init__(self):
        self.connected = False
        self.com = None
        self.comList = {}
        self.baudRate = 57600
        self.serialPorts()
        self.debug = True
        self.sender = None
        
        self.x = axis('X', self)
        self.y = axis('Y', self)
        self.z = axis('X', self)
    
    def serialPorts(self):
        # find all available serial device names
        for each in range(10):
            try:
                serial.Serial(each)
                self.comList[serial.device(each)] = each
            except:
                pass
        return self.comList
    
    def isConnected(self):
        try:
            self.sender.write('G21')
        except:
            return False
        return True
    
    def close(self):
        self.sender.ser.close()
        self.sender = None
    
    def write(self, gcode):
        try:
            self.sender.write(gcode)
        except:
            self.close()
        
    def read(self):
        try:
            return self.sender.read()
        except:
            self.close()
        
    def connect( self, serialDevice, baudRate=57600 ):
        self.com = serialDevice
        self.baudRate = baudRate
        
        self.sender = RepRapArduinoSerialSender.RepRapArduinoSerialSender( self.com , str(self.baudRate) , True)
        self.sender.reset()
        
        time.sleep(1)
        
        self.write('G21')
        self.write('G90')
        
        
        
    
        