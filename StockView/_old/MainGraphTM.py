from PyQt5.QtCore import Qt, QLineF, QRectF
from PyQt5.QtGui import QPen,  QColor

class MainGraphTM:
    def __init__(self):
        pass
    
    def ComputeRange(self):
        # x Range
        self.view_start_x = (int)(float(self.start_px) / self.zoom)
        self.view_end_x = (int)(float(self.start_px + self.rect.width()) / self.zoom)
        
        count = len(self.data['date'])
        if self.view_start_x < 0:
            self.view_start_x = 0
        if self.view_start_x > count-1:
            self.view_start_x = count-1
        if self.view_end_x < 0:
            self.view_end_x = 0
        if self.view_end_x > count-1:
            self.view_end_x = count-1        
        
        # y range
        if self.view_end_x > self.view_start_x :
            self.range_min = min(self.data['low'][self.view_start_x : self.view_end_x+1])
            self.range_max = max(self.data['high'][self.view_start_x : self.view_end_x+1])
        else:
            self.view_min = 10
            self.view_max = 100

        range = self.range_max - self.range_min
        self.view_min = self.range_min - range * 0.1
        self.view_max = self.range_max + range * 0.1
        
    def BuildTransformation(self,  painter):
        painter.resetTransform()
        
        # Translate
        height = self.rect.height()
        
        painter.translate(self.rect.x(),  self.rect.y())
        painter.translate(-self.start_px,  height)
        painter.scale(self.zoom,  float(height)/(self.view_max - self.view_min))
        painter.translate(0,  self.view_min)
        painter.scale(1,  -1)        
    
    def Draw(self,  data, rect,  start_px,  zoom,  painter):
        self.data = data
        self.rect = rect
        self.start_px = start_px
        self.zoom = zoom
        
        # compute range
        self.ComputeRange()

        self.BuildTransformation(painter)

        #
        self.DrawCandleStickGraph2( self.data,  self.view_start_x,  self.view_end_x,  painter,  0)
        if zoom > 2.8:
            self.DrawCandleStickGraph2( self.data,  self.view_start_x,  self.view_end_x,  painter,  1)
            
        
        self.DrawTest(painter)
        
        painter.resetTransform()
        
    def DrawTest(self,  painter):
        # draw rect
        pen = QPen(Qt.darkGreen)
        pen.setCosmetic(True)
        painter.setPen(pen)

        painter.drawLine(QLineF(self.view_start_x,  self.view_min,  self.view_end_x,  self.view_min))
        painter.drawLine(QLineF(self.view_start_x,  self.view_max,  self.view_end_x,  self.view_max))

        painter.drawLine(QLineF(self.view_start_x,  self.view_min,  self.view_start_x,  self.view_max))
        painter.drawLine(QLineF(self.view_end_x,  self.view_min,  self.view_end_x,  self.view_max))

    #######################
    #
    #  方法1 直接绘制
    #
    #######################    
    def DrawCandleStickGraph1(self, data,  start_x,  end_x,  painter,  ipass):
        w = 0.35
        
        OPEN = data['open']
        CLOSE = data['close']
        HIGH = data['high']
        LOW = data['low']
        
        colors = (QColor(Qt.red),  QColor(Qt.darkGreen),  QColor(Qt.black))
        
        for i in range(start_x,  end_x+1):
            px = float(i)+w
        
            yhigh = HIGH[i];
            ylow = LOW[i];
            yopen = OPEN[i];
            yclose = CLOSE[i];
            
            diff = yclose-yopen
            if diff > 0.005:
                type = 0
            elif diff < -0.005:
                type = 1
            else:
                type =2
            
            if ipass == 0:
                #绘制引线
                pen = QPen();
                pen.setCosmetic(True)
                pen.setColor(colors[type])
                painter.setPen(pen)
                painter.drawLine(QLineF(px,  ylow,  px,  yhigh))
            else:
                # 绘制块
            
                if type == 2:
                    pen = QPen();
                    pen.setCosmetic(True)
                    pen.setColor(colors[type])
                    painter.setPen(pen)
                    painter.drawLine(QLineF(px-w,  yclose,  px+w,  yclose))
                else:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(colors[type])
                    if yclose > yopen:
                        painter.drawRect(QRectF(px-w,  yopen,  w+w,  yclose-yopen))
                    else:
                        painter.drawRect(QRectF(px-w,  yclose,  w+w,  yopen-yclose))  
                    

    #######################
    #
    #  方法2 批量绘制
    #
    #######################    
    def DrawCandleStickGraph2(self, data,  start_x,  end_x,  painter,  ipass):
        w = 0.35
        
        OPEN = data['open']
        CLOSE = data['close']
        HIGH = data['high']
        LOW = data['low']
        
        list = ([],  [],  [])
        #colors = (QColor(Qt.red),  QColor(Qt.darkGreen),  QColor(Qt.black))
        
        # 创建绘制列表
        for i in range(start_x,  end_x+1):
            px = float(i)+w
        
            yhigh = HIGH[i];
            ylow = LOW[i];
            yopen = OPEN[i];
            yclose = CLOSE[i];
            
            diff = yclose-yopen
            if diff > 0.005:
                type = 0
            elif diff < -0.005:
                type = 1
            else:
                type = 2

            
            if ipass == 0:
                #绘制引线
                list[type].append(QLineF(px,  ylow,  px,  yhigh))
            else:
                # 绘制块
                if type == 0:
                    list[type].append(QRectF(px-w,  yopen,  w+w,  yclose-yopen))
                elif type == 1:
                    list[type].append(QRectF(px-w,  yclose,  w+w,  yopen-yclose))
                else:
                    list[type].append(QLineF(px-w,  yclose,  px+w,  yclose))
                    

        # 实际绘制
        if ipass == 0:
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
        
        else:
            painter.setPen(Qt.NoPen)
            
             # 红色
            painter.setBrush(Qt.red)
            painter.drawRects(list[0])
            
            # 绿色
            painter.setBrush(Qt.darkGreen)
            painter.drawRects(list[1])
            
            # 黑色
            if list[2]:
                pen = QPen();
                pen.setCosmetic(True)
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawLines(list[2])           
