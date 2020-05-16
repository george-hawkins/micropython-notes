import machine
import time

pin13 = machine.Pin(13, machine.Pin.OUT)
on = 1 
while True:
    pin13.value(on)
    on ^= 1
    time.sleep(0.2)
