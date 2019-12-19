from collections import deque
import csv
import logging
import numpy as np
import os
import time

logger = logging.getLogger(__name__)

def validateConfig(config):
        if not config:
            config = {}
        if not 'dataFiles' in config:
            config['dataFiles'] = ['xdata.csv', 'ydata.csv', 'isMandelbrot.csv']
        if not 'maxIter' in config:
            config['maxIter'] = 80 # Max number of iterations for mandelbrot set check
        if not 'stepSizes' in config:
            config['stepSizes'] = [1e-3, 1e-3] # x-axis, y-axis
        if not 'xlimits' in config:
            config['xlimits'] = [-2, 1]
        if not 'ylimits' in config:
            config['ylimits'] = [-2, 2]
        return config

class MandelbrotSet:
    def __init__(self, config = None):
        self.config = validateConfig(config)

        if self.hasDataFile():
            [xdata, ydata, isMandelbrot] = self.loadData()
        else:
            [xdata, ydata, isMandelbrot] = self.generateData()

        self.xdata = xdata
        self.ydata = ydata
        self.isMandelbrot = isMandelbrot

    @staticmethod
    def recurrenceEq(z, c):
        return z ** 2 + c

    def getMandelbrotSet(self):
        return [self.xdata, self.ydata, self.isMandelbrot]

    def generateMandelbrotSet(self, xmin, xmax, ymin, ymax):
        assert(xmin < xmax and ymin < ymax)
        [xstep, ystep] = self.config['stepSizes']
        xpoints = np.arange(xmin, xmax, xstep)
        ypoints = np.arange(ymin, ymax, ystep)

        xsize, = xpoints.shape
        ysize, = ypoints.shape

        xdata = np.tile(xpoints, (ysize, 1))
        ydata = np.transpose(np.tile(ypoints, (xsize, 1)))
        assert(xdata.shape == ydata.shape)

        cdata = xdata + ydata * 1j

        # Iterative approach
        isMandelbrot = np.zeros(cdata.shape)
        logger.info(f'grid size: {xsize}x{ysize}')

        totalStartTime = time.time()
        for y in range(0, ysize):
            # rowStartTime = time.time()
            for x in range(0, xsize):
                isMandelbrot[y][x] = self.checkPointForMandelbrotSet(cdata[y][x])
            # rowEndTime = time.time()
            # logger.info(f'row {y} takes: {rowEndTime - rowStartTime}s')
        totalEndTime = time.time()
        logger.info(f'total time: {totalEndTime - totalStartTime}s')
        return [xdata, ydata, isMandelbrot]
        # isMandelbrot = self.isMandelbrotVectorized(cdata)


    def checkPointForMandelbrotSet(self, c, points = None):
        '''Check whether a point is in Mandelbrot set, with side effects
           that update auxiliary information.
           @params
           c: a complex number representing the point to check
           points: if not None, track the points during recurrence calc.
           @return: True if c is in Mandelbrot set. Otherwise False.
        '''
        maxIter = self.config['maxIter']
        z = np.complex(0, 0)
        CACHE_SIZE = 9
        firstPointsQueue = deque(maxlen=CACHE_SIZE)
        lastPointsQueue = deque(maxlen=CACHE_SIZE)
        firstPointsQueue.append(z)
        lastPointsQueue.append(z)
        isMandelbrot = True # assume true
        for _ in range(0, maxIter):
            zNext = MandelbrotSet.recurrenceEq(z, c)
            lastPointsQueue.append(zNext)
            if len(firstPointsQueue) < CACHE_SIZE:
                firstPointsQueue.append(zNext)
            if (np.absolute(zNext)) > 2:
                isMandelbrot = False
                break
            z = zNext
        
        if points != None:
            queue = lastPointsQueue if isMandelbrot else firstPointsQueue
            for elem in queue:
                points.append([elem.real, elem.imag])
        
        return isMandelbrot

    def isMandelbrotVectorized(self, cdata):
        pass


    def hasDataFile(self):
        dataFiles = self.config['dataFiles']
        assert(len(dataFiles) == 3)
        for filename in dataFiles:
            if not os.path.exists(filename):
                return False
        return True


    def loadData(self):
        def readFromCSV(filename):
            data = []
            with open(filename, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    data.append(row)
            return np.array(data)
    
        dataFiles = self.config['dataFiles']
        [xdata, ydata, isMandelbrot] = list(map(readFromCSV, dataFiles))
        return [xdata, ydata, isMandelbrot]


    def generateData(self):
        def writeToCSV(filename, data):
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter = ' ')
                writer.writerows(data)

        [xmin, xmax] = self.config['xlimits']
        [ymin, ymax] = self.config['ylimits']
        [xdata, ydata, isMandelbrot] = self.generateMandelbrotSet(xmin, xmax, ymin, ymax)
        [writeToCSV(filename, data) for filename, data in zip(self.config['dataFiles'], [xdata, ydata, isMandelbrot])]
        return [xdata, ydata, isMandelbrot]