from PyQt5.QtCore import Qt, QLineF
from PyQt5.QtGui import QPen,  QColor, QPainter,  QPicture
from .BlockManager import *

#
# 
# 除K线图以外
# 辅助图形主要分为连续数据(series) 和 非连续的数据(discrete)
#
#

from enum import Enum
class SeriesType(Enum):
    LINE = 0
    BAR = 1
    CANDLESTICK = 2
    
class RangeMode(Enum):
    ZERO_TO_MAX = 0
    ABS_MAX = 1
    MIN_MAX = 2
    

###################
#
# Draw Indicator For Consecutive Data
#
# 连续的数据图形量巨大，但是规律
# 可以使用“块”优化策略，解决Python调用GUI十分严重的性能问题
# Use block method to optimize performance
#
###################
class IndicatorGraphConsecutive:
    BLOCK_SIZE_SHIFT = 8
    
    def __init__(self,  indicator = None):
        self.indicator = indicator
        #self.Build()
        
    def Build(self,  dc):
        if not self.indicator:
            return
        
        # 调用 indicator 求值函数
        self.LEN = self.indicator.LEN
        self.indicator.EvalFn()
        
        # build blocks
        self.bm = BlockManager(self.LEN)
        for block in self.bm.blocks(0,  self.LEN):
            self.BuildBlock( block,  dc)
            self.BuildBlockRanges(block)

    def BuildBlock(self, block, dc ):
        drawLineQueue = QPicture()
        painter = QPainter()
        painter.begin(drawLineQueue)
        # Draw
        for (type, color, S) in self.indicator.SERIES:
            lines = None
            if type == SeriesType.LINE:
                lines = self.DrawLineSeries(S,  block.start_x,  block.end_x)
            elif type == SeriesType.BAR:
                lines = self.DrawBarSeries(S,  block.start_x,  block.end_x)

            pen = QPen(color)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLines(lines)

        painter.end()
        block.drawLineQueue = drawLineQueue       

    def BuildBlockRanges(self, block ):
        maxs = []
        mins =[]        # Compute range
        # MINS
        for S in self.indicator.MINS:
            # Skip to valid value
            for begin in range(block.start_x,  block.end_x):
                if S[begin] !=None: break
            mins.append(min(S[begin:block.end_x]))
        # MAXS
        for S in self.indicator.MAXS:
            # Skip to valid value
            for begin in range(block.start_x,  block.end_x):
                if S[begin] !=None: break
            maxs.append(max(S[begin:block.end_x]))
        # 汇总
        block.y_min = min(mins) if mins else 0
        block.y_max = max(maxs)
        
    def Draw(self, view, dc):
        painter = dc.painter
        
        # Clipping 一定要在Transform之前做，否则会被影响
        if view.isClipping:
          painter.setClipRect(view.rect)
        # Setup Matrix
        painter.setTransform(view.tm)
        #
        for block in self.bm.blocks(view.view_start_x,  view.view_end_x):
            painter.drawPicture(0, 0,  block.drawLineQueue)
            
        # Restore
        painter.resetTransform()
        painter.setClipping(False)

    def ComputeRange(self,  view):
        ############
        maxs = []
        mins =[]
        
        #
        for block in self.bm.blocks(view.view_start_x,  view.view_end_x):
            mins.append(block.y_min)
            maxs.append(block.y_max)
        
        mode = self.indicator.RANGE_MODE
        if mode == RangeMode.ZERO_TO_MAX:
            view.view_min = 0
            view.view_max = max(maxs)
        elif mode == RangeMode.ABS_MAX:
            abs_v = [abs(v) for v in (mins+maxs)]
            absmax = max(abs_v)
            view.view_min = -absmax
            view.view_max = absmax
        elif mode == RangeMode.MIN_MAX:
            view.view_min = min(mins)
            view.view_max = max(maxs)
        
        return (view.view_min ,  view.view_max)

    def DrawBarSeries(self,  Y,  start_x,  end_x):
        
        lines = []
        for x in range(start_x, end_x ):
            if Y[x] == None:
                continue
            y = Y[x]
            
            l = QLineF(x, 0,  x,  y  )
            lines.append(l)
        
        return lines

    def DrawLineSeries(self,  Y,  start_x,  end_x):
        
        if end_x > len(Y) - 1:
            end_x = len(Y) - 1
    
        lines = []
        for x in range(start_x, end_x ):
            if Y[x] == None:
                continue
            y1 = Y[x]
            y2 = Y[x+1]
            
            l = QLineF(x, y1,  x+1,  y2  )
            lines.append(l)
    
        return lines

class IndicatorGraphConsecutiveGL(IndicatorGraphConsecutive):
    def __init__(self, indicator):
        super().__init__(indicator)

    def BuildBlock(self, block,  dc):
        GL = dc.GL
        
        block.list_ = GL.glGenLists(1)
        GL.glNewList(block.list_, GL.GL_COMPILE)
        
        # Draw
        for (type, color, S) in self.indicator.SERIES:
            lines = None
            qc = QColor(color)
            if type == SeriesType.LINE:
                lines = self.DrawLineSeries(S,  block.start_x,  block.end_x)
                self.DrawLinesGL(lines, qc, GL)
            elif type == SeriesType.BAR:
                lines = self.DrawBarSeries(S,  block.start_x,  block.end_x)
                self.DrawLinesGL(lines, qc, GL)
            elif type == SeriesType.CANDLESTICK:
                self.DrawCandleGraphGL(block, GL, 0)

        GL.glEndList()


    def DrawLinesGL(self, lines, qc, GL ):
        GL.glColor3f(qc.redF(),  qc.greenF(),  qc.blueF());
        GL.glBegin(GL.GL_LINES);
        for line in lines:
            GL.glVertex2f(line.x1(), line.y1());
            GL.glVertex2f(line.x2(), line.y2());
        GL.glEnd()
    
    def DrawRectListGL(self, rectlist, qc, GL ):
        GL.glColor3f(qc.redF(),  qc.greenF(),  qc.blueF());
        for rect in rectlist:
            GL.glBegin(GL.GL_QUADS);
            GL.glVertex2f(rect.x(), rect.y());
            GL.glVertex2f(rect.x(), rect.bottom());
            GL.glVertex2f(rect.right(), rect.bottom());
            GL.glVertex2f(rect.right(), rect.y());
            GL.glEnd()

    def Draw(self,  view,  dc):
        GL = dc.GL
        
        x = view.rect.x()
        y = view.fullRect.height() - view.rect.y() - view.rect.height()
        w = view.rect.width()
        h = view.rect.height()

        GL.glViewport(x, y, w, h)        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

        view_start_x = (int)(view.tx / view.zoom)
        view_end_x = (int)((view.tx + view.rect.width()) / view.zoom)     
        GL.glOrtho( view_start_x, view_end_x, view.view_min, view.view_max, 0, 1)

        for block in self.bm.blocks(view.view_start_x,  view.view_end_x):
            GL.glCallList(block.list_)     


###################
#
# Draw Indicator For Discrete Data
#
# 绘图量少并且不规律
# 所以使用直接绘制的方法
#
###################

class IndicatorGraphDiscrete:
    def __init__(self):
        pass
        
