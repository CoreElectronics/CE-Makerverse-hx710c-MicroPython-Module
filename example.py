from machine import Pin
from Makerverse_hx710c import Makerverse_hx710c
from time import sleep_ms

LC = Makerverse_hx710c(dataPin = Pin(17), clkPin = Pin(16), calibration=1.4397e-3)

while True:
    Data = LC.read_hx710_calibrated()
    print("{:+.3f} g".format(Data))
    sleep_ms(90)

