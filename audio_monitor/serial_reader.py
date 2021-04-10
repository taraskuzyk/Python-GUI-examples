"""
this is a stripped down version of the SWHear class.
It's designed to hold only a single audio sample in memory.
check my githib for a more complete version:
    http://github.com/swharden
"""

import serial, os, pty
import time
import numpy as np
from threading import Thread
import random


class SpoofSerial:
    """
    Creates some sine function for testing the GUI in variables *x* and *y*
    """
    def __init__(self, freq=1, time_interval=2.0, period=0.016, generate_noise=False, snr=0.1):

        self.freq = freq
        self.time_interval = time_interval
        self.period = period
        self.generate_noise = generate_noise
        self.snr = snr

        self.x = np.arange(0, time_interval, period)
        self.y = np.sin(2 * np.pi * self.x * freq)

        self.dont_touch_me = False

        self.paused = False
        self.t = Thread(target=self.run_stream)

    def start(self):
        """Starts running a stream on a new thread"""
        self.t.start()

    def run_stream(self):
        """Begins streaming a sine in *x* and *y*"""
        while not self.paused:
            time.sleep(self.period)

            self.dont_touch_me = True

            new_x_val = self.x[-1] + 1.0 * self.period
            self.x = np.append(self.x, [new_x_val])

            new_y_val = np.sin(2 * np.pi * new_x_val * self.freq)
            if self.generate_noise:
                new_y_val *= 1 + random.uniform(-self.snr, self.snr)

            self.y = np.append(self.y, [new_y_val])

            self.dont_touch_me = False

    def pause(self):
        """Temporarily stops updating the sine, but the values are still kept"""
        self.paused = True

    def unpause(self):
        """Continue updating the sine"""
        self.paused = False


if __name__ == "__main__":
    print("Hi")
    try:
        thing = SpoofSerial(time_interval=1, period=0.5)
        print("hi")

        thing.start()
        while True:
            print(thing.x, thing.y)
    except KeyboardInterrupt:
        print("Exiting...")
        exit()
