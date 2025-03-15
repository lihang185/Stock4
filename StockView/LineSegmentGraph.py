from PyQt5.QtCore import Qt, QLineF, QRectF,  QRect
from PyQt5.QtGui import QPen,  QColor, QPainter,  QPicture
from .BlockManager import *
from .GraphEngine import *
import math


###################
#
# Draw Indicator For Discrete Data
#
# 绘图量少并且不规律
# 所以使用直接绘制的方法
#
###################

class LineSegmentData():
    def __init__(self, rs, M):
        self.M = M
        timeAxis = M['TimeAxis']
        self.BuildLineData(rs, timeAxis)
        
    def FindSlow(T, idate):
        if idate < T[0]:
            return -1, 0
        
        for i in range(len(T)):
            if idate < T[i]:
                return 0, i
                
        return 1, 0
    
    def BuildLineData(self, data, timeAxis):
        list = []
        
        for idate, y in data:
            # find in T
            x = timeAxis.FindDate(idate)
            item = (x, y, idate)
            list.append(item)
            
        self.data = list
        
    def BuildLineSegment(self, data, multi):
        list = [(x, y*multi) for x, y, d in data]
        return list
        
    def EvalFn(self):
        #
        self.RANGE_MODE = RangeMode.MIN_MAX
        self.MINS = []
        self.MAXS = []
        
        self.M1 = self.BuildLineSegment(self.data, 1.0)
        self.M1_5 = self.BuildLineSegment(self.data, 1.4142)
        self.M2 = self.BuildLineSegment(self.data, 2.0)
        self.M4 = self.BuildLineSegment(self.data, 4.0)
        self.M6 = self.BuildLineSegment(self.data, 5.6568)
        self.M8 = self.BuildLineSegment(self.data, 8.0)
        self.M16 = self.BuildLineSegment(self.data, 16.0)
        
        self.SERIES = [
            (SeriesType.LINE_SEGMENT,  Qt.black, self.M1),  
            (SeriesType.LINE_SEGMENT,  Qt.darkCyan, self.M1_5),  
            (SeriesType.LINE_SEGMENT,  Qt.blue, self.M2),  
            (SeriesType.LINE_SEGMENT,  Qt.red, self.M4),  
            (SeriesType.LINE_SEGMENT,  Qt.darkMagenta, self.M6),  
            (SeriesType.LINE_SEGMENT,  Qt.black, self.M8),  
            (SeriesType.LINE_SEGMENT,  Qt.darkYellow, self.M16),  
        ]
        

class LineSegmentGraph():
    def __init__(self,  indicator):
        self.indicator = indicator
    
    def Build(self,  view, dc):
        if not self.indicator:
            return
            
        self.indicator.EvalFn()
        
        log11 = math.log(1.1)

        self.line_list = []
        for tp, color, data in self.indicator.SERIES:
            newlist = []
            LEN = len(data)
            for x in range(LEN-1):
                x1, y1 = data[x]
                x2, y2 = data[x+1]
                if view.log_coord:
                    y1 = math.log(y1)/log11
                    y2 = math.log(y2)/log11
                line = QLineF(x1, y1, x2, y2)
                newlist.append(line)
            
            item = (color, newlist)
            self.line_list.append(item)
        
    #######################
    #    Drawing
    #
    #######################  
    def Draw(self, view, dc):
        painter = dc.painter
        
        # Clipping 一定要在Transform之前做，否则会被影响
        if view.isClipping:
            painter.setClipRect(view.rect)
        # Setup Matrix
        GraphEngine.SetupTransform(view, painter)
        #
        
        for color, list in self.line_list:
            GraphEngine.EmitDrawLinesQt(list, color, painter)
            
        # Restore
        painter.resetTransform()
        painter.setClipping(False)
        
class LineSegmentGraphGL(LineSegmentGraph):
    def __init__(self,  indicator):
        self.indicator = indicator
        
    def Draw(self, view, dc):
        GL = dc.GL
        
        GraphEngineGL.SetupTransformGL(view, dc.GL)
        
        GL.glLineWidth(view.line_width)
        GL.glDisable(GL.GL_LINE_SMOOTH)

        for color, list in self.line_list:
            GraphEngineGL.EmitDrawLinesGL(list, color, dc.GL)
            
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(1)
