from pyo import *
from time import sleep
import random

s = Server(duplex=1)
s.setOutputDevice(8)
s.boot()
s.start()

# Compute the duration, in seconds, of one buffer size.
buftime = s.getBufferSize() / s.getSamplingRate()

# Delay parameters
delay_time_l = Sig(0.125)  # Delay time for the left channel delay.
delay_time_l.ctrl()
delay_feed = Sig(0.75)  # Feedback value for both delays.
delay_feed.ctrl()

# Because the right delay gets its input sound from the left delay, while
# it is computed before (to send its output sound to the left delay), it
# will be one buffer size latrigte. To compensate this additional delay on the
# right, we substract one buffer size from the real delay time.
delay_time_r = Sig(delay_time_l, add=-buftime)

# Setup up a soundfile player.
sf = SfPlayer("Tumtum.aif", loop=True).stop()
sf.mix(2).out()

right = Delay(Sig(0), delay=delay_time_r).out(1)
left = Delay(Sig(0), delay=delay_time_r).out(0)


def add_delay():
    global left, right
    right = Delay(Sig(0), delay=delay_time_r).out(1)
    left = Delay(sf + right * delay_feed, delay=delay_time_l).out()
    original_delayed = Delay(sf, delay_time_l, mul=1 - delay_feed)
    right.setInput(original_delayed + left * delay_feed)


def stop_delay():
    right.stop()
    left.stop()
    sf.stop()
    sf.mix(2).out()
    sf.play()


sf.play()
add_delay()
sleep(4)
stop_delay()
sleep(3)
add_delay()
sleep(5)


