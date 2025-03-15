from PyQt5.QtCore import Qt, QLine, QLineF, QRectF,  QRect
from PyQt5.QtGui import QPen,  QColor, QPainter,  QPicture
from .BlockManager import *
from .config import *
#
# 
# 除K线图以外
# 辅助图形主要分为连续数据(series) 和 非连续的数据(discrete)
#
#

from enum import Enum
class SeriesType(Enum):
    
    LINE = 1
    BAR = 2
    VOL = 3
    LINE_P = 4

    CANDLESTICK = 6

    LINE_SEGMENT = 9
    
class RangeMode(Enum):
    ZERO_TO_MAX = 0
    ABS_MAX = 1
    MIN_MAX = 2
    MAIN_GRAPH = 10
    

###################
#
# Draw Indicator For Consecutive Data
#
# 连续的数据图形量巨大，但是规律
# 可以使用“块”优化策略，解决Python调用GUI十分严重的性能问题
# Use block method to optimize performance
#
###################

import math
log11 = math.log(1.1)

class GraphEngineBase:
    BLOCK_SIZE_SHIFT = 8
    
    def __init__(self,  indicator = None):
        self.indicator = indicator
        #self.Build()
        
    #######################
    #    BUILD
    #
    #######################  
    def Build(self, view, dc):
        if not self.indicator:
            return
        
        # 调用 indicator 求值函数
        self.LEN = self.indicator.LEN
        self.indicator.EvalFn()
        self.log_coord = view.log_coord
        
        # build blocks
        self.bm = BlockManager(self.LEN)
        for block in self.bm.blocks(0,  self.LEN):
            self.BuildDrawQueue( block, self.indicator.SERIES, 0, dc)
            self.BuildBlockRanges(block)
        
        if hasattr(self.indicator, 'SERIES_DETAIL'):
            for block in self.bm.blocks(0,  self.LEN):
                self.BuildDrawQueue( block, self.indicator.SERIES_DETAIL, 1, dc)

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

    #######################
    #    DRAW
    #
    #######################  
    def Conv(self, y):
        log_y = math.log(y)/log11 if self.log_coord else y
        return log_y


    def DrawBarSeries(self,  Y,  start_x,  end_x):
        
        lines1 = []
        lines2 = []
        for x in range(start_x, end_x ):
            if Y[x] == None:
                continue
            y = self.Conv(Y[x])
            
            l = QLineF(x, 0,  x,  y  )
            if y > 0:
                lines1.append(l)
            else:
                lines2.append(l)
        
        return (lines1, lines2)

    def DrawVOLSeries(self,  Y, start_x,  end_x):
        
        list_ = []
        for x in range(start_x, end_x ):
            if Y[x] == None:
                continue
            y = self.Conv(Y[x])
            
            l = QLineF(x, 0,  x,  y  )
            list_.append(l)
        
        return list_

    def DrawLineSeries(self,  Y,  start_x,  end_x):
        
        if end_x > len(Y) - 1:
            end_x = len(Y) - 1
    
        lines = []
        for x in range(start_x, end_x ):
            if Y[x] == None:
                continue
            y1 = self.Conv(Y[x])
            y2 = self.Conv(Y[x+1])
            
            l = QLineF(x, y1,  x+1,  y2  )
            lines.append(l)
    
        return lines

    #######################
    #    RANGE
    #
    #######################  
    def ComputeRange(self,  view):
        ############
        maxs = []
        mins =[]
        
        #
        for block in self.bm.blocks(view.start_x,  view.end_x):
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
        else:
            assert 0, "Not define vfunc ComputeRange(view)"

        return (view.view_min ,  view.view_max)
        
class GraphEngine(GraphEngineBase):

    #######################
    #    Build DrawQueue
    #
    #######################  
    def BuildDrawQueue(self, block, SERIES, ipass, dc ):
        drawQueue = QPicture()
        painter = QPainter()
        painter.begin(drawQueue)
        # Draw
        for (stype, color, S, P) in SERIES:
            lines = None
            if stype == SeriesType.LINE:
                lines = self.DrawLineSeries(S,  block.start_x,  block.end_x)
                GraphEngine.EmitDrawLinesQt(lines, color, painter)
            elif stype == SeriesType.LINE_P:
                if block.start_x < P:
                    block.start_x = P
                lines = self.DrawLineSeries(S,  block.start_x,  block.end_x)
                GraphEngine.EmitDrawLinesQt(lines, color, painter)
            elif stype == SeriesType.BAR:
                (lines1, lines2)= self.DrawBarSeries(S,  block.start_x,  block.end_x)
                GraphEngine.EmitDrawLinesQt(lines1, colorSchemes['red'], painter)
                GraphEngine.EmitDrawLinesQt(lines2, colorSchemes['green'], painter)
            elif stype == SeriesType.VOL:
                lines= self.DrawVOLSeries(S, block.start_x,  block.end_x)
                GraphEngine.EmitDrawLinesTypesQt(lines, P, color, painter)
            elif stype == SeriesType.CANDLESTICK:
                self.BuildCandleGraphQt(block.start_x,  block.end_x, painter, ipass)

        painter.end()
        if ipass == 0:
            block.drawQueue = drawQueue
        else:
            block.drawQueueDetail = drawQueue

    def EmitDrawLinesQt(list_, color, painter):
        pen = QPen(color)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(list_)

    def EmitDrawLinesTypesQt(list_, types_, color, painter):
        for line, t in zip(list_, types_):
            c = colorSchemes['red'] if t == 0 else color
            pen = QPen(c)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLine(line)

    def EmitDrawRectsQt(list_, color, painter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawRects(list_)


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
        #for block in self.bm.list:
        for block in self.bm.blocks(view.start_x,  view.end_x):
            painter.drawPicture(0, 0,  block.drawQueue)
            if view.zoom > 2.8 and hasattr(block, 'drawQueueDetail'):
                painter.drawPicture(0, 0,  block.drawQueueDetail)
            
        # Restore
        painter.resetTransform()
        painter.setClipping(False)

    def SetupTransform(view, painter):
        ##################
        # 由于setWindow使用整数参数
        #    直接使用会损失很大的经度
        # 所以通过整体放大100倍
        #   来提高经度，效果显著
        ##################
        painter.resetTransform()
        painter.translate(0, 0.75)
        painter.scale(100, -100)

        rect = QRect()
        rect.setLeft(view.view_start_x*100)
        rect.setRight(view.view_end_x*100)
        rect.setTop(-view.view_max*100)
        rect.setBottom(-view.view_min*100)

        
        painter.setWindow( rect )
        painter.setViewport(view.rect)
        
    def SetupTransform2D(self, view, dc):
        pass
        
    #######################
    #    Gird
    #
    ####################### 
    def DrawGrid(self,  view,  dc):
        painter = dc.painter
        # Setup Matrix
        GraphEngine.SetupTransform(view, painter)
        # Draw Gird
        pen1 = QPen(Qt.gray)
        pen1.setCosmetic(True)
        pen1.setStyle(Qt.DotLine)
        pen2 = QPen(Qt.red)
        pen2.setCosmetic(True)
        pen2.setStyle(Qt.DotLine)
        for (y,  ylog, py,  type) in view.axis:
            if type == 0:
                painter.setPen(pen1)
            else:
                painter.setPen(pen2)
        
            # ** BUG **
            # 调用drawLine如果第一个参数传入Int
            # 类型，那么整个对象会使用Int，在后面的
            # 运算中会严重损失经度变心，普通坐标系
            # 看不出来，但是放在对数坐标非常明显
            #painter.drawLine(view.view_start_x,  ylog, view.view_end_x,  ylog)
            
            line = QLineF(view.view_start_x,  ylog, view.view_end_x,  ylog)
            painter.drawLine(line)
        # Restore
        painter.resetTransform()
        painter.setClipping(False)

class GLDrawList:
    def __init__(self,  list_,  GL):
        self.list_ = list_
        self.GL = GL
        
    def __del__(self):
        if self.list_:
            self.GL.glDeleteLists(self.list_, 1);
        
    def get(self):
        return self.list_

class GraphEngineGL(GraphEngine):

    #######################
    #  Build DrawQueue
    #
    #######################  
    def BuildDrawQueue(self, block, SERIES, ipass, dc):
        GL = dc.GL
        
        list_ = GL.glGenLists(1)
        GL.glNewList(list_, GL.GL_COMPILE)
        
        # Draw
        for (stype, color, S, P) in SERIES:
            lines = None
            if stype == SeriesType.LINE:
                lines = self.DrawLineSeries(S,  block.start_x,  block.end_x)
                GraphEngineGL.EmitDrawLinesGL(lines, color, GL)
            elif stype == SeriesType.LINE_P:
                if block.start_x < P:
                    block.start_x = P
                lines = self.DrawLineSeries(S,  block.start_x,  block.end_x)
                GraphEngineGL.EmitDrawLinesGL(lines, color, GL)
            elif stype == SeriesType.BAR:
                lines1, lines2 = self.DrawBarSeries(S,  block.start_x,  block.end_x)
                GraphEngineGL.EmitDrawLinesGL(lines1, colorSchemes['red'], GL)
                GraphEngineGL.EmitDrawLinesGL(lines2, colorSchemes['green'], GL)
            elif stype == SeriesType.VOL:
                lines = self.DrawVOLSeries(S, block.start_x,  block.end_x)
                GraphEngineGL.EmitDrawLinesTypesGL(lines, P, color, GL)
            elif stype == SeriesType.CANDLESTICK:
                self.BuildCandleGraphGL(block, GL, ipass)

        GL.glEndList()
        
        if ipass == 0:
            block.list_1 = GLDrawList(list_, GL)
        else:
            block.list_2 = GLDrawList(list_, GL)
            
    
    def EmitDrawLinesGL(lines, color, GL ):
        qc = QColor(color)
        GL.glColor3f(qc.redF(),  qc.greenF(),  qc.blueF());
        GL.glBegin(GL.GL_LINES);
        for line in lines:
            GL.glVertex2f(line.x1(), line.y1());
            GL.glVertex2f(line.x2(), line.y2());
        GL.glEnd()

    def EmitDrawLinesTypesGL(lines, types, color, GL ):
        GL.glBegin(GL.GL_LINES);
        for line, t in zip(lines, types):
            c = colorSchemes['red'] if t == 0 else color
            qc = QColor(c)
            GL.glColor3f(qc.redF(),  qc.greenF(),  qc.blueF());
            GL.glVertex2f(line.x1(), line.y1());
            GL.glVertex2f(line.x2(), line.y2());
        GL.glEnd()

    
    def EmitDrawRectsGL(rectlist, color, GL ):
        qc = QColor(color)
        GL.glColor3f(qc.redF(),  qc.greenF(),  qc.blueF());
        for rect in rectlist:
            GL.glBegin(GL.GL_QUADS);
            GL.glVertex2f(rect.x(), rect.y());
            GL.glVertex2f(rect.x(), rect.bottom());
            GL.glVertex2f(rect.right(), rect.bottom());
            GL.glVertex2f(rect.right(), rect.y());
            GL.glEnd()
        
    #######################
    #  Drawing
    #
    #######################  
    def Draw(self,  view,  dc):
        GL = dc.GL
        
        ################
        # glViewport 自带Clip 功能
        # 所以设置好矩阵后就可以了
        GraphEngineGL.SetupTransformGL(view, dc.GL)

        for block in self.bm.blocks(view.start_x,  view.end_x):
            GL.glCallList(block.list_1.get())     
            if view.zoom > 2.8 and hasattr(block, 'list_2'):
                GL.glCallList(block.list_2.get())
        
    def SetupTransformGL(view, GL):
        x = view.rect.x()
        y = view.fullRect.height() - view.rect.y() - view.rect.height()
        w = view.rect.width()
        h = view.rect.height()

        GL.glViewport(x, y, w, h)        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

        GL.glOrtho( view.view_start_x, view.view_end_x, view.view_min, view.view_max, 0, 1)
    
    def SetupTransform2D(self, view, dc):
        GL = dc.GL
        
        x = view.rect.x()
        y = view.fullRect.height() - view.rect.y() - view.rect.height()
        w = view.rect.width()
        h = view.rect.height()

        GL.glViewport(x, y, w, h)        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho( -0.5, w-1+0.5, h-1+0.5, -0.5, 0, 1)
    
        #############
        # frame test
        #############
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glBegin(GL.GL_LINES);
        # top
        GL.glVertex2d(0, 0);
        GL.glVertex2d(w, 0);
        # bottm
        GL.glVertex2d(0, h-1);
        GL.glVertex2d(w, h-1);        
        #left
        GL.glVertex2d(0, 0);
        GL.glVertex2d(0, h);
        #right
        GL.glVertex2d(w-1, 0);
        GL.glVertex2d(w-1, h);
        GL.glEnd();    
        
    #######################
    #  Gird
    #
    ####################### 
    stipple = 0x1111
    def DrawGrid(self,  view,  dc):
        GL = dc.GL
        
        GL.glEnable(GL.GL_LINE_STIPPLE) 
        GL.glLineStipple(1, self.stipple)
        GL.glBegin(GL.GL_LINES);
        
        for (y, ylog,  py,  type) in view.axis:
            if type == 0:
                GL.glColor3f(0.7, 0.7, 0.7)
            else:
                GL.glColor3f(1.0, 0.0, 0.0)
            # OpenGL 屏幕坐标是 “Y轴反转的” 的
            # 并且用的是viewport坐标
            #h = py - view.rect.y() -0.5 if proj else ylog
            #py = view.ProjectToScreenY_GL(y)
            GL.glVertex2f(view.view_start_x, ylog);
            GL.glVertex2f(view.view_end_x, ylog);
        GL.glEnd();
        
        GL.glDisable(GL.GL_LINE_STIPPLE) 

        GL.glEnd();    
    
