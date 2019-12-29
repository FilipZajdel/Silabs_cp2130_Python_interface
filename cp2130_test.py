from cp2130 import CP2130
import time

if __name__ == "__main__":
    cp = CP2130()
    cp.open()

    while True:
        time.sleep(.2)
        print(cp.getEventCounter())
        if cp.getEventCounter()%2 == 0:
            cp.setGpioValueAndMode(0, 1, 0)
        else:
            cp.setGpioValueAndMode(0, 1, 1)