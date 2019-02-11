import colorsys
import math
import time
import random

try:
    import unicornhathd
    print("unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhathd

def colourise(val):
    # loud is red, quiessent is blue, green is in the middle
    if val > 190:
        colour = (val, 0, 0)
    elif val >=85 and val <= 190:
        colour = (0, val, 0)
    else:
        colour = (0, 0, val)
    return colour

try:
    while True:
        for x in range(0,16):
            for y in range(0,16):
                ind = 16*x + y
                val = random.randint(0,255)#signal[ind]
                r,g,b = colourise(val)
                unicornhathd.set_pixel(x, y, r, g, b)
        unicornhathd.show()
        time.sleep(0.1)
except KeyboardInterrupt:
    unicornhathd.off()
