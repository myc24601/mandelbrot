from mandelbrot import MandelbrotSet
import matplotlib.pyplot as plt
import numpy as np
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO, 
    format="%(levelname)s %(name)s: %(message)s",
    stream=sys.stdout)

logger = logging.getLogger(__name__)

config = {'stepSizes': [1e-2, 1e-2]}
mbs = MandelbrotSet(config)

[xdata, ydata, isMandelbrot] = mbs.getMandelbrotSet()
cdata = 1 - isMandelbrot

# drawStartTime = time.time()
fig = plt.figure()
plt.scatter(xdata.flatten(), ydata.flatten(), c = cdata.flatten())
plt.gray()
plt.setp(plt.gca(), autoscale_on=False)

def drawSequence(event):
    if (event.inaxes):
        xpos = event.xdata
        ypos = event.ydata
        seq = []
        checkStartTime = time.time()
        mbs.checkPointForMandelbrotSet(np.complex(xpos, ypos), seq)
        xseq, yseq = zip(*seq)
        checkEndTime = time.time()
        logger.info(f'check time: {checkEndTime - checkStartTime}s')
 
        if drawSequence.lineH:
            for line in drawSequence.lineH:
                line.remove()
        drawSequence.lineH = plt.plot(xseq, yseq, 'b-', linewidth=1, marker='o', markeredgecolor='r', markerfacecolor='r', markersize=2)
        fig.canvas.draw()

drawSequence.lineH = None

fig.canvas.mpl_connect('button_press_event', drawSequence)
plt.show()
# plt.show(block=False)
# plt.close()
# drawEndTime = time.time()
# logger.info(f'plot time: {drawEndTime - drawStartTime}s')
