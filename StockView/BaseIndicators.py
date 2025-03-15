from PyQt5.QtCore import Qt, QLineF
from PyQt5.QtGui import QColor
# indicator

import numpy as np
from .GraphEngine import *

class MACD:
    def __init__(self, data):
        self.LEN = data['data_length']
        self.data = data['close']
        
        self.SHORT = 12
        self.LONG = 26
        self.MID = 9
        
    def EvalFn(self):
        self.DIF = MACD.EMA(self.data, self.SHORT) - MACD.EMA(self.data, self.LONG)
        self.DEA = MACD.EMA(self.DIF, self.MID)
        self.MACD = ( self.DIF - self.DEA ) * 2
        
        # Add to compute range
        self.RANGE_MODE = RangeMode.ABS_MAX
        self.MINS = [self.DIF]
        self.MAXS = [self.DIF]
        
        # Add to draw list
        self.SERIES = [
            (SeriesType.LINE,  QColor(60, 60, 60), list(self.DIF), None),  
            (SeriesType.LINE,  QColor(0, 121, 213), list(self.DEA), None), 
            (SeriesType.BAR,  Qt.black, list(self.MACD), None)
         ]
        
    def EMA(X,  N):
        LEN = len(X)
        Y = np.zeros(LEN)
        
        for i in range(0, LEN):
            yp = X[i] if i == 0 else Y[i-1]
            # Y=(X*2+Y'*(N-1))/(N+1)
            Y[i] = (X[i] * 2 + yp * (N-1)) / (N+1)
            
        return Y
        
class KDJ:
    def __init__(self, data):
        self.LEN = data['data_length']
        self.CLOSE = data['close']
        self.HIGH = data['high']
        self.LOW = data['low']
        
        self.N = 9
        self.M1 = 3
        self.M2 = 3
        
    def EvalFn(self):
        self.RSV = (self.CLOSE - KDJ.LLV(self.LOW, self.N)) / (KDJ.HHV(self.HIGH, self.N) - KDJ.LLV(self.LOW, self.N)) * 100
        self.K = KDJ.SMA(self.RSV, self.M1, 1)
        self.D = KDJ.SMA(self.K, self.M2, 1)
        self.J = self.K * 3.0 - self.D * 2.0
        
        # Add to compute range
        self.RANGE_MODE = RangeMode.MIN_MAX
        self.MINS = [self.J]
        self.MAXS = [self.J]
        
        # Add to draw list
        self.SERIES = [
            (SeriesType.LINE,  QColor(60, 60, 60), list(self.K), None),  
            (SeriesType.LINE,  QColor(0, 121, 213), list(self.D), None), 
            (SeriesType.LINE,  QColor(128, 0, 128), list(self.J), None)
         ]
    
    def SMA(X, N, M):
        LEN = len(X)
        Y = np.zeros(LEN)
        
        for i in range(0, LEN):
            yp = X[i] if i == 0 else Y[i-1]
            # Y=(X*M+Y'*(N-M))/N
            Y[i] = (X[i] * M + yp * (N-M)) / N
            
        return Y
        
    def LLV(X, N):
        LEN = len(X)
        Y = np.zeros(LEN)
        for i in range(LEN):
            start = i-(N-1)
            if start < 0: start = 0
            Y[i] = min(X[start:i+1])
        return Y
        
    def HHV(X, N):
        LEN = len(X)
        Y = np.zeros(LEN)
        for i in range(LEN):
            start = i-(N-1)
            if start < 0: start = 0
            Y[i] = max(X[start:i+1])
        return Y
        
class VOLIndicator:
    def __init__(self,  data):
        self.LEN = data['data_length']
        self.vol = data['vol']
        self.type = data['type']

    def EvalFn(self):
        VOL = (SeriesType.VOL, QColor(0, 74, 105), self.vol, self.type)

        self.RANGE_MODE = RangeMode.ZERO_TO_MAX
        self.MAXS = [self.vol]
        self.MINS = []
        self.SERIES = [VOL]
        return self.SERIES

class MAIndicator:
    def __init__(self, data):
        self.LEN = data['data_length']
        self.data = data['close']
        
    def EvalFn(self):
        # MA
        self.ma5 = ( SeriesType.LINE_P,  QColor(60, 60, 60), MAIndicator.MA(self.data, 5), 4 )
        self.ma10 = ( SeriesType.LINE_P,  QColor(0, 121, 213), MAIndicator.MA(self.data, 10), 9 )
        self.ma30 = ( SeriesType.LINE_P,  QColor(128, 0, 128), MAIndicator.MA(self.data, 30), 29 )
        self.ma60 = ( SeriesType.LINE_P,  QColor(128, 128, 128), MAIndicator.MA(self.data, 60), 59 )

        self.RANGE_MODE = RangeMode.MIN_MAX
        self.MINS = [self.data]
        self.MAXS = [self.data]
        self.SERIES = [self.ma5,  self.ma10,  self.ma30,  self.ma60]
        return self.SERIES
    
    def MA(D,  days):
        LEN = len(D)
        Y = np.zeros(LEN)
        for i in range(0, LEN):
            if i - (days-1) < 0 :
                Y[i] = D[i]
            else:
                v = 0
                for j in range(days):
                    v += D[i-j]
                Y[i] = (v/days)
                
        return Y

# ma = [v +1  for v in data['close']]
