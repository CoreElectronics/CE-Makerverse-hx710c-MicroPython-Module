from Makerverse_hx710c import Makerverse_hx710c
from time import sleep_ms

# The calibration value needs to be measured for each load cell.
# See the guide for details: https://core-electronics.com.au/tutorials/makerverse-load-cell-kit.html
LC = Makerverse_hx710c(calibration= 0.001420345)

while True:
    Data = LC.read_hx710_averaged(N=5)
    print("{:+.3f} g".format(Data))
    sleep_ms(90)

