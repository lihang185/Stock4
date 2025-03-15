from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .drawcandle import BuildCandleStickGraphBuffer

class MainGraphDR:
    def __init__(self):
        self.c_api_backend = False
        pass
    
    def ProjectCoordSystem(self,  value):
        return value
    def UnProjectCoordSystem(self,  value):
        return value
        
    def ProjX(self,  x):
        px = int(float(x) * self.zoom)
        return px - self.StartPx
        
    def Proj2X(self,  px):
        return (int)(float(px) / self.zoom)
        
    def GetStartIndex(self):
        start_index = self.Proj2X(self.StartPx) + 1
        if start_index < 0:
            start_index = 0
        return start_index
        
    def GetEndIndex(self):
        end_index = self.Proj2X(self.StartPx + self.rect.width())
        if end_index > len(self.data['date'])-1:
            end_index = len(self.data['date'])-1
        return end_index
  
    
    def ProjectToPy(self,  value):
        if value < 0.1:
            value = 0.1
        logv = self.ProjectCoordSystem(value)
        #logv = value
        
        py_inv = (int)((logv - self.y_min) / (self.y_max - self.y_min) * self.rect.height());
        return self.rect.height() - 1 - py_inv
    
    def ProjectToY(self,  py):
        py_inv = (self.rect.height() - py) - 1;
        value = py_inv * (self.y_max - self.y_min) / self.rect.Height + self.y_min;
        return self.UnProjectCoordSystem(value);
        
    def UpdateData(self,  data):
        pass
    
    def Compute(self,  data,  view):
        self.data = data
        self.StartPx = view.StartPx
        self.zoom = view.zoom  
        self.rect = view.rect()

        self.ComputeRange( view)
    
    def ComputeRange(self):
        self.view_start_x = self.GetStartIndex()
        self.view_end_x = self.GetEndIndex()
        
        value_min = min(self.data['LOW'][self.view_start_x : self.view_end_x])
        value_max = max(self.data['HIGH'][self.view_start_x : self.view_end_x])

        self.y_min = self.ProjectCoordSystem(value_min)
        self.y_max = self.ProjectCoordSystem(value_max)
        
        self.y_range = self.y_max - self.y_min
        if self.y_range <= 0:
            self.y_min = self.ProjectCoordSystem(10)
            self.y_max = self.ProjectCoordSystem(100)
        else:
            self.y_min = self.y_min - self.y_range * 0.1
            self.y_max = self.y_max + self.y_range * 0.1
    
    def Draw(self,  rect,  start_px,  zoom,  painter):
        self.rect = rect
        self.StartPx = start_px
        self.zoom = zoom
        
        self.ComputeRange()
        
        ##############
        # Candle width
        ##############
        if self.zoom < 4 :
            candle_width = 1
        elif self.zoom < 7 :
            candle_width = 3
        elif self.zoom < 10:
            candle_width = 5
        else:
            candle_width = 7    
        
        ##############
        #  Draw Backend
        ##############
        self.c_api_backend = True
       
        if self.c_api_backend:
            self.DrawCandleStickGraph_CAPI( data,  self.view_start_x,  self.view_end_x, painter,  candle_width)
        else:
            self.DrawCandleStickGraph( data,  self.view_start_x,  self.view_end_x, painter,  candle_width)

    #######################
    #
    #  方法1  批量快速绘制
    #
    #######################

    def DrawCandleStickGraph(self,  data,  start_x,  end_x,  painter,  candle_width):
   
        
        ##############
        # Pass1: 绘制引线
        ##############
        list = self.BuildCandleStickToBuffer(data,  start_x,  end_x,  painter, candle_width,  0)
        if True :
            pen = QPen();
            pen.setCosmetic(True)
            painter.setPen(pen)
            
            # 红色
            pen.setColor(Qt.red)
            painter.setPen(pen)
            painter.drawLines(list[0])
            
            # 绿色
            pen.setColor(Qt.darkGreen)
            painter.setPen(pen)
            painter.drawLines(list[1])
            
            # 黑色
            if list[2]:
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawLines(list[2])
        
        ##############
        # Pass2: 绘制方块
        ##############
        if candle_width != 1 :
            list = self.BuildCandleStickToBuffer(data,  start_x,  end_x,  painter, candle_width, 1)
            pen = QPen();
            pen.setCosmetic(True)
            painter.setPen(pen)
            
            # 红色
            pen.setColor(Qt.red)
            painter.setPen(pen)
            painter.drawLines(list[0])
            
            # 绿色
            pen.setColor(Qt.darkGreen)
            painter.setPen(pen)
            painter.drawLines(list[1])
            
            # 黑色
            if list[2]:
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawLines(list[2])
        
                    



    def BuildCandleStickToBuffer(self,  data,  start_x,  end_x,  painter,  candle_width,  ipass  ):
        if False:
            OPEN = data['open']
            CLOSE = data['close']
            HIGH = data['high']
            LOW = data['low']
        else:
            OPEN = data['OPEN']
            CLOSE = data['CLOSE']
            HIGH = data['HIGH']
            LOW = data['LOW']
        
        c = 0
        e = candle_width
        if candle_width == 1 :
            c = 0
        elif candle_width == 3 :
            c = 1
        elif candle_width == 5 :
            c = 2
        else:
            c = 3
        
        list = ([],  [],  [])
        
        for i in range(start_x ,  end_x):
            px = self.ProjX(i)
            
            diff = CLOSE[i] - OPEN[i]

            # 上涨或下跌
            if diff > 0.005:
                type = 0
            elif diff < -0.005:
                type = 1
            else:
                type =2

            if ipass == 0:
                yhigh = self.ProjectToPy(HIGH[i]);
                ylow = self.ProjectToPy(LOW[i]);
                #绘制引线
                list[type].append(QLineF(px+c,  ylow,  px+c,  yhigh))
            else:
                yopen = self.ProjectToPy(OPEN[i]);
                yclose = self.ProjectToPy(CLOSE[i]);
                # 绘制块
                if type == 2:
                    list[type].append( QLineF(px,  yclose,  px+e,  yclose))
                else:
                    for x in range(0,  e):
                        if x != c:
                            list[type].append( QLineF(px+x,  yopen,  px+x,  yclose))
                            
        return list



       
       
    #######################
    #
    #  方法2 C_API 优化
    #
    #######################
    def DrawCandleStickGraph_CAPI(self,  data,  start_x,  end_x,  painter,  candle_width):
        
        
        d = {'open': data['OPEN'],  'high': data['HIGH'],  'low': data['LOW'],  'close': data['CLOSE'] }
        
        list = BuildCandleStickGraphBuffer(d , start_x, end_x,  self.y_min,  self.y_max,  self.rect.width(),  self.rect.height(), self.StartPx,  self.zoom,  candle_width,  QLineF)
        
        if True :
            pen = QPen();
            pen.setCosmetic(True)
            painter.setPen(pen)
            
            # 红色
            pen.setColor(Qt.red)
            painter.setPen(pen)
            painter.drawLines(list[0])
            
            # 绿色
            pen.setColor(Qt.darkGreen)
            painter.setPen(pen)
            painter.drawLines(list[1])
            
            # 黑色
            if list[2]:
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawLines(list[2])



    
