from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MainGraph:
    def __init__(self):
        pass
    
    def ProjectCoordSystem(self,  value):
        return value
    def UnProjectCoordSystem(self,  value):
        return value
        
    def ProjX(self,  x):
        px = int(float(x) * self.zoom)
        return px - self.StartPx
    
    def ProjectToPy(self,  value):
        if value < 0.1:
            value = 0.1
        logv = self.ProjectCoordSystem(value)
        
        py_inv = (int)((logv - self.view_min) / (self.view_max - self.view_min) * self.rect.height());
        return self.rect.height() - 1 - py_inv
    
    def ProjectToY(self,  py):
        py_inv = (self.rect.height() - py) - 1;
        value = py_inv * (self.view_max - self.view_min) / self.rect.Height + self.view_min;
        return self.UnProjectCoordSystem(value);
    
    def Compute(self,  data,  view):
        self.data = data
        self.StartPx = view.StartPx
        self.zoom = view.zoom  

        self.ComputeRange( view)
    
    def ComputeRange(self,   view):
        self.range_min = min(self.data['low'][view.StartX: view.EndX])
        self.range_max = max(self.data['high'][view.StartX: view.EndX])

        self.view_min = self.ProjectCoordSystem(self.range_min)
        self.view_max = self.ProjectCoordSystem(self.range_max)
        
        range = self.view_max - self.view_min
        if range <= 0:
            self.view_min = self.ProjectCoordSystem(10)
            self.view_max = self.ProjectCoordSystem(100)
        else:
            self.view_min = self.view_min - range * 0.1
            self.view_max = self.view_max + range * 0.1
    
    def Draw(self,  data,  view,  painter):
        self.data = data
        self.StartPx = view.StartPx
        self.zoom = view.zoom
        self.rect = view.rect()
        
        self.DrawCandleStickGraph(view,  painter)

    
    def DrawCandleStickGraph(self,  view,  painter):
        
        OPEN = self.data['open']
        CLOSE = self.data['close']
        HIGH = self.data['high']
        LOW = self.data['low']
        
        for i in range(view.StartX,  view.EndX):
            px = self.ProjX(i)
            
            #open = OPEN[i]
            #close = CLOSE[i]
            
            yhigh = self.ProjectToPy(HIGH[i]);
            ylow = self.ProjectToPy(LOW[i]);
            yopen = self.ProjectToPy(OPEN[i]);
            yclose = self.ProjectToPy(CLOSE[i]);
            self.DrawCandleStick(px,  yhigh,  ylow,  yopen,  yclose,  painter)
        
    def DrawCandleStick(self, px,  high,  low,  open,  close,  painter  ):
        c = self.CandleStickCenter()
        e = self.CandleStickWidth()
        
        #绘制引线
        painter.drawLine(px+c,  low,  px+c,  high)
        if open == close:
            painter.drawLine(px,  close,  px+e,  close)
        else:
            for x in range(0,  e):
                if x == c:
                    continue
                painter.drawLine(px+x,  open,  px+x,  close)
        
    def CandleStickWidth(self):
        if self.zoom < 4 :
            return 1
        elif self.zoom < 7 :
            return 3
        elif self.zoom < 10:
            return 5
        else:
            return 7
    
    def CandleStickCenter(self):
        if self.zoom < 4 :
            return 0
        elif self.zoom < 7 :
            return 1
        elif self.zoom < 10:
            return 2
        else:
            return 3
