from pyo import *
from time import sleep


s = Server(duplex=1, nchnls=1)

s.setOutputDevice(8)
s.boot()
s.start()
sf = SfPlayer("/home/boo/src/photonbit/technochaman/sounds/Torm.aif", speed=1, loop=True).out()
sleep(2)
sf2 = SfPlayer("/home/boo/src/photonbit/technochaman/sounds/Tumtum.aif", speed=1, loop=True).out()



