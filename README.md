# Makerverse Load Cell ADC MicroPython Module

This is the firmware repo for the Core Electronics [Makerverse Load Cell ADC](https://core-electronics.com.au/catalog/product/view/sku/ce08248) MicroPython module.

See the [Makerverse Load Cell Kit](https://core-electronics.com.au/tutorials/makerverse-load-cell-kit.html) for more documentation.

# Usage

## Examples

The example below assumes that Sclk and Dout are connected to GPIO16 and GPIO17, respectively. It reads values from the load cell ADC and prints an **estimate** of the weight in grams.

For higher accuracy, the calibration procedure in the [guide](https://core-electronics.com.au/tutorials/makerverse-load-cell-kit.html) can be followed.

```python
from Makerverse_hx710c import Makerverse_hx710c
from time import sleep_ms

LC = Makerverse_hx710c(dataPin = Pin(17), clkPin = Pin(16), calibration=1.4397e-3)

while True:
    Data = LC.read_hx710()
    print("{:+.3f} g".format(Data))
    sleep_ms(90)
```

## Details - Makerverse_hx710c Class

### Constructor: Makerverse_hx710c(dataPin = Pin(17), clkPin = Pin(16), stateMachine = 0, skipTest = False, calibration=1.4397e-3)

Returns a Makerverse_hx710c object to interface with a Load Cell ADC module connected to the specified pins.

Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
dataPin | Pin object | 0 to 28 | Pin(17) | The Raspberry Pi Pico pin which is connected to the Load Cell ADC's Dout pin.
dirPin | Pin object | 0 to 28 | Pin(16) | The Raspberry Pi Pico pin which is connected to the Load Cell ADC's Sclk pin.
stateMachine | int | 0 to 3 | 0 | The RP2040 state machine to use for the HX710C data interface. Only change if your project requires more than one PIO driver.
skipTest | Boolean | True or False | False | By default this object constructor tests for the presence of a HX710C chip, reads 10 values, and takes the average as the "zero" point. If skipTest = True this is not done. The variable Makerverse_hx710c.zero can be set with a raw ADC value to change the zero point.
calibration | float | 1e-3 to 2e-3 (typical) | 1.4379e-3 | The load cell calibration value in units of grams per least significant bit. This value was measured on a sample load cell but is only an approximation for any given load cell. 

### read_hx710_calibrated(relativeToZero = True)

Returns a floating point value equal to the mass measured by the load cell in units of **grams**. The accuracy of the returned value depends on the accuracy of the calibration.

This function is blocking and will wait for an ADC reading to become available before returning. It can take up to 100ms to return.

Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
relativeToZero | Boolean | True or False | True | When set to True the internal variable Makerverse_hx710c.zero is subtracted from the ADC reading. The intention is for an empty load cell platform to result in a measurement of zero. The zero point is initialised on object creation so long as skipTest = False was used by the constructor.

### read_hx710(relativeToZero = True)

Returns a the next available raw ADC value minus the zero point. The raw value is a 24-bit 2's complement number from 0x800000 to 0x7FFFFF (decimal -8388608 to 8388607). The zero point is typically relatively close to zero but can cause the return value to exceed the specified range.

This function is blocking and will wait for an ADC reading to become available before returning. It can take up to 100ms to return.

Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
relativeToZero | Boolean | True or False | True | When set to True the internal variable Makerverse_hx710c.zero is subtracted from the ADC reading. The intention is for an empty load cell platform to result in a measurement of zero. The zero point is initialised on object creation so long as skipTest = False was used by the constructor.


### read_hx710_averaged(N = 10)

Returns the average of several readings to achieve greater measurement precision. Note that the **accuracy** (derived from the accuracy of the calibration procedure) remains unchanged.

When using this function you may wish to consider first taking a "large" number of samples of the zero point. The zero point measured at initialisation only uses an average of 10 readings.

Note that the noise in ADC readings is closely Gaussian. As such, noise decreases with the square root of the number of samples in the average. To halve the error the number of averaged samples must increase by a factor of 4.

This function is blocking and will wait for all required ADC readings to become available before returning. It can take up to 100ms per averaged sample to return.

Note that 32 samples can be buffered in the PIO' FIFO. If readings are not being streamed from the ADC then 32 samples should be read and discarded directly before calling this function to ensure that the most recent values are used.

Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
N | int | 1 to inf | 10 | The number of samples to read before calculating and returning an average.

### calibrate(weight = 50, samples = 50)

This method performs a calibration procedure to measure the sensitivity of the load cell and load cell ADC in units of grams per least significant bit.

The calibration procedure requires a calibration reference mass. The Makerverse Load Cell Kit contains a 50g mass with an error far below the 0.1g resolution of the hardware provided with the Makerverse Load Cell Kit.

If requied, 50g calibration mass is available individually and has SKU [CE08490](https://core-electronics.com.au/catalog/product/view/sku/ce08490).

This method can be used with a calibration mass of any size. The ideal mass is one equal to the full scale measurement of the load cell, in the kit's case 3kg, but this is impractical for the kit.

Multiple 50g masses can be placed on the load cell platform simultaneously for increased accuracy. The 0.1g accuracy is only realised for measurements **below** the calibration mass.

With a single 50g calibration mass the approximate absolute error at 3kg is around +/- 6g (0.2%).

Parameter | Type | Range | Default | Description
--- | --- | --- | --- | ---
weight | float | 0 to 3000 | 50 | The weight of the calibration mass placed on the scales during the calibration procedure, units of grams.
samples | int | 1 to inf | 50 | The number of samples to average when measuring the calibration mass. Note that the noise spectrum of the ADC is not "white" - there can be relatively high magnitude, long time scale, thermal drift in the ADC and load cell which is more significant than sample-to-sample noise.