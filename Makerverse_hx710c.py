import rp2
from machine import Pin
import array
import time

class Makerverse_hx710c():
    @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, set_init=rp2.PIO.IN_LOW)
    def hx710_pio_10Hz():
        wrap_target()
        wait(0,pin,0)
        nop() .side(1) [1]
        
        set(x,8)
        label("signExtension")
        in_(pins, 1) # Read MSB 8 times, performs sign extension from 24-bit to 32-bit signed int
        jmp(x_dec, "signExtension")
        in_(pins, 1) .side(0) [0] # First bit of 24-bit data
        
        set(x, 22)
        label("loop")
        nop() .side(1) [1]
        in_(pins, 1) .side(0) [0]    
        jmp(x_dec, "loop")
        nop() .side(1) [0]
        push()
        nop() .side(0) [1]
        
        wrap()
        
    def __init__(self, dataPin = Pin(17), clkPin = Pin(16), stateMachine = 0, skipTest = False, calibration=1.4397e-3):
        self.sm = rp2.StateMachine(stateMachine, self.hx710_pio_10Hz, freq=2_000_000, sideset_base=clkPin, in_base=dataPin)
        self.sm.active(1)
        self.zero = 0 # Dummy value; measured and reassigned below.
        self.calibration = calibration
        # Read 10 elements and make sure they aren't all zero and that it takes about 100ms
        
        if skipTest is False:
            tmpData = [0]*10
            start = time.ticks_ms()
            while dataPin.value() == 1:
                if time.ticks_ms() - start > 500:
                    raise RuntimeError("Load Cell ADC timeout - check wiring")
            for i in range(10):
                tmpData[i] = self.read_hx710()
            end = time.ticks_ms()
            timeLength_ms = end - start
            
            if all([ v == 0 for v in tmpData ]):
                raise RuntimeError("Load cell ADC is only returning zeros - check wiring")
            
            if timeLength_ms < 100:
                raise RuntimeError("Load cell returned 10 readings in under 100ms - check wiring")
            
            self.zero = int(round(sum(tmpData) / len(tmpData)))
        
    def calibrate(self, weight=50, samples=50):
        print("Remove any weight from the load cell platform and press Enter")
        tmp = input()
        print("Measuring the zero point...")
        
        # Empty the PIO FIFO
        for k in range(32):
            tmp = self.read_hx710()
        
        zeroRaw = 0
        for k in range(samples):
            print("Reading value ", k, " of ", samples)
            zeroRaw += self.read_hx710()
        zeroRaw = zeroRaw / samples
        print("Add the ", weight, "g calibration mass then press Enter")
        tmp = input()
        print("Measuring calibration point...")
        # Empty the PIO FIFO
        for k in range(32):
            tmp = self.read_hx710()
        weightRaw = 0
        for k in range(samples):
            print("Reading value ", k, " of ", samples)
            weightRaw += self.read_hx710()
        weightRaw /= samples
        
        cal = weight/(weightRaw - zeroRaw)
        self.calibration = cal
        print("Load cell calibrated.")
        print("The calibration value is: ", cal, " grams per LSB")
        print("add 'calibration=",cal,"' keyword argument to the call to Makerverse_hx710c() to make this value permanent.")
        print("Press Enter to end the calibration procedure.")
        tmp = input()
      
    def zero(self, N = 1):
        total = 0
        for i in range(N):
            total += self.read_hx710(relativeToZero = False)
        total /= N
        self.zero = total
        
    def read_hx710(self, relativeToZero = True):
        # Passing sm.get() through an integer array converts 32-bit sign-extended data
        # to a signed integer
        if relativeToZero is True:
            return array.array('i', [self.sm.get()])[0] - self.zero
        else:
            return array.array('i', [self.sm.get()])[0]
        
    def read_hx710_calibrated(self, relativeToZero = True):
        return self.read_hx710(relativeToZero) * self.calibration
    
    def read_hx710_averaged(self, N = 10):
        s = 0
        for i in range(N):
            s += self.read_hx710()
        s /= N
        return s*self.calibration