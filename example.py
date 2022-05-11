from Makerverse_hx710c import Makerverse_hx710c
from time import sleep_ms

LC = Makerverse_hx710c(calibration= 0.001420345)

# LC.calibrate()

while True:
    Data = LC.read_hx710_averaged(N=5)
    # 8.91864e-4 is a calibrated value
    # Converts ADC LSBs to grams
    #print("{:+.2f} g".format(Data*8.91864e-4))
    print("{:+.3f} g".format(Data))
    sleep_ms(90)
    #print(Data)

