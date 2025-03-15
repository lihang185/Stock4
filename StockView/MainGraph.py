from PyQt5.QtCore import Qt, QLineF, QRectF
from PyQt5.QtGui import QPen,  QColor, QPainter,  QPicture


from .GraphEngine import *
    
class MainGraphBase:
    def EvalFn(self):
        # Add to compute range
        self.RANGE_MODE = RangeMode.MAIN_GRAPH
        self.MINS = [self.data['low']]
        self.MAXS = [self.data['high']]
        
        # Add to draw list
        self.SERIES = [
            (SeriesType.CANDLESTICK,  Qt.black, self.data, None),  
        ]
        self.SERIES_DETAIL = self.SERIES
        
    def ComputeRange(self,  view):
        maxs = []
        mins =[]
        
        #
        for block in self.bm.blocks(view.start_x,  view.end_x):
            mins.append(block.y_min)
            maxs.append(block.y_max)

            if view.log_coord:
                low = self.Conv(min(mins))
                high = self.Conv(max(maxs))
                range = (high-low) * self.margin / 100.0
                low -=  range
                high += range
                view.view_min = low
                view.view_max = high
            else:
                view.view_min = min(mins)
                view.view_max = max(maxs)


    #######################
    #
    #  K线图 Candle Stick 方法2
    #
    #######################    
    def DrawCandleStickSeries( self, start_x,  end_x,  ipass):
        w = 0.35
        
        data = self.data
        TYPE = data['type']
        OPEN = data['open']
        CLOSE = data['close']
        HIGH = data['high']
        LOW = data['low']
        
        list = ([],  [],  [])
        #colors = (QColor(Qt.red),  QColor(Qt.darkGreen),  QColor(Qt.black))
        
        # 创建绘制列表
        for i in range(start_x,  end_x):
            px = float(i)
            
            type = TYPE[i]

            if ipass == 0:
                #绘制引线
                yhigh = self.Conv(HIGH[i]);
                ylow = self.Conv(LOW[i]);
                list[type].append(QLineF(px,  ylow,  px,  yhigh))
            else:
                # 绘制块
                yopen = self.Conv(OPEN[i]);
                yclose = self.Conv(CLOSE[i]);
                if type == 0:
                    list[type].append(QRectF(px-w,  yopen,  w+w,  yclose-yopen))
                elif type == 1:
                    list[type].append(QRectF(px-w,  yclose,  w+w,  yopen-yclose))
                else:
                    list[type].append(QLineF(px-w,  yclose,  px+w,  yclose))
                        
        return list
      

class MainGraph(MainGraphBase, GraphEngine):
    def __init__(self,  data):
        self.data = data
        self.LEN = data['data_length']
        self.margin = 25.0
        
        # 
        super().__init__(self)

    def BuildCandleGraphQt( self, start_x,  end_x,  painter,  ipass):
        list = self.DrawCandleStickSeries( start_x,  end_x, ipass )
        
        # 实际绘制
        if ipass == 0:
            # 红色
            GraphEngine.EmitDrawLinesQt(list[0], colorSchemes['red'], painter )
            # 绿色
            GraphEngine.EmitDrawLinesQt(list[1], colorSchemes['green'], painter )
            # 黑色
            GraphEngine.EmitDrawLinesQt(list[2], colorSchemes['black'], painter )
        else:
            # 红色
            pen = QPen(colorSchemes['red'])
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(colorSchemes['background'])
            painter.drawRects(list[0])
            # 绿色
            GraphEngine.EmitDrawRectsQt(list[1], colorSchemes['green'], painter )
            # 黑色
            GraphEngine.EmitDrawLinesQt(list[2], colorSchemes['black'], painter )            


class MainGraphGL(MainGraphBase, GraphEngineGL):
    def __init__(self,  data):
        self.data = data
        self.LEN = data['data_length']
        self.margin = 25.0
        
        # 
        super().__init__(self)

    def BuildCandleGraphGL( self, block,  GL,  ipass):
        list = self.DrawCandleStickSeries( block.start_x,  block.end_x, ipass )

        # 实际绘制
        if ipass == 0:
            # 红色
            GraphEngineGL.EmitDrawLinesGL(list[0], colorSchemes['red'], GL)
            # 绿色
            GraphEngineGL.EmitDrawLinesGL(list[1], colorSchemes['green'], GL)
            # 黑色
            GraphEngineGL.EmitDrawLinesGL(list[2], colorSchemes['black'], GL)
        else:
            # 红色
            GraphEngineGL.EmitDrawRectsGL(list[0], colorSchemes['red'], GL)
            # 绿色
            GraphEngineGL.EmitDrawRectsGL(list[1], colorSchemes['green'], GL)
            # 黑色
            GraphEngineGL.EmitDrawLinesGL(list[2], colorSchemes['black'], GL)

