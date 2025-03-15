from PyQt5.QtCore import Qt, QLineF, QRectF
from PyQt5.QtGui import QPen,  QColor,  QPainter,  QPicture

from .config import *
from .BlockManager import *

class MainGraph:
    def __init__(self,  data):
        self.data = data
        self.LEN = data['data_length']
        self.bm = None

    def Build(self,  dc):
        # Iterator function
        self.bm = BlockManager(self.LEN)
        for block in self.bm.blocks(0,  self.LEN):
            self.BuildBlock( block, dc)

    def BuildBlock(self, block, dc):
        drawLineQueue = QPicture()
        painter = QPainter()
        painter.begin(drawLineQueue)
        self.DrawCandleGraphNormal(block.start_x, block.end_x ,  painter,  0)
        painter.end()
        
        drawRectQueue = QPicture()
        painter.begin(drawRectQueue)
        self.DrawCandleGraphNormal( block.start_x, block.end_x ,  painter,  1)
        painter.end()
        
        # set draw element
        block.drawLineQueue = drawLineQueue
        block.drawRectQueue = drawRectQueue
        # set range
        block.ymin = min(self.data['low'][block.start_x : block.end_x])
        block.ymax = max(self.data['high'][block.start_x : block.end_x])



    def ComputeRange(self,  view):

        ###########
        # 计算y值范围
        ###########

        calc_mins = []
        calc_maxs = []
        
        for block in self.bm.blocks(view.view_start_x,  view.view_end_x):
            calc_mins.append(block.ymin)
            calc_maxs.append(block.ymax)
      
        # y range
        if calc_mins and calc_maxs:
            self.range_min = min(calc_mins)
            self.range_max = max(calc_maxs)
        else:
            self.view_min = 10
            self.view_max = 100

        _range = self.range_max - self.range_min
        view.view_min = self.range_min - _range * 0.1
        view.view_max = self.range_max + _range * 0.1
        
        return (view.view_min, view.view_max)


#        for block in self.bm.blocks(0,  self.LEN):
#            
#            if ( iblock == start_block and view.view_start_x != 0 )or (iblock == end_block and view.view_end_x != LEN-1):
#
#                start_x = block.start_x if block.start_x > view.view_start_x else view.view_start_x
#                end_x = block.end_x if block.end_x < view.view_end_x else view.view_end_x
#                
#                if end_x > start_x:
#                    calc_mins.append(min(self.data['low'][start_x : end_x]))
#                    calc_maxs.append(max(self.data['high'][start_x : end_x]))
#
#            else:
#                calc_mins.append(block.ymin)
#                calc_maxs.append(block.ymax)


    def Draw(self,  view,  dc):
        painter = dc.painter
        
        # Clipping 一定要在Transform之前做，否则会被影响
        if view.isClipping:
          painter.setClipRect(view.rect)
        # Setup Matrix
        painter.setTransform(view.tm)

        for block in self.bm.blocks(view.view_start_x,  view.view_end_x):
            
            painter.drawPicture(0,  0,  block.drawLineQueue)
            if view.zoom > 2.8:
                painter.drawPicture(0,  0,  block.drawRectQueue)
        
        # Restore Maxtrix and Clip
        painter.resetTransform()
        painter.setClipping(False)
        

    def DrawCandleGraphNormal( self, start_x,  end_x,  painter,  ipass):
        
        list = self.DrawCandleStickGraph( start_x,  end_x, ipass )

        # 实际绘制
        if ipass == 0:
            pen = QPen()
            pen.setCosmetic(True)
            painter.setPen(pen)
            
            # 红色
            pen.setColor(colorSchemes['red'])
            painter.setPen(pen)
            painter.drawLines(list[0])
            
            # 绿色
            pen.setColor(colorSchemes['green'])
            painter.setPen(pen)
            painter.drawLines(list[1])
            
            # 黑色
            if list[2]:
                penblack = QPen(colorSchemes['black']);
                penblack.setCosmetic(True)
                painter.setPen(penblack)
                painter.drawLines(list[2])
        
        else:
            
            # 红色
            pen = QPen(colorSchemes['red'])
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(colorSchemes['background'])
            painter.drawRects(list[0])
            
            # 绿色
            painter.setPen(Qt.NoPen)
            painter.setBrush(colorSchemes['green'])
            painter.drawRects(list[1])
            
            # 黑色
            if list[2]:
                pen = QPen();
                pen.setCosmetic(True)
                pen.setColor(colorSchemes['black'])
                painter.setPen(pen)
                painter.drawLines(list[2])           

    #######################
    #
    #  方法2 批量绘制
    #
    #######################    
    def DrawCandleStickGraph( self, start_x,  end_x,  ipass):
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
                yhigh = HIGH[i];
                ylow = LOW[i];
                list[type].append(QLineF(px,  ylow,  px,  yhigh))
            else:
                # 绘制块
                yopen = OPEN[i];
                yclose = CLOSE[i];
                if type == 0:
                    list[type].append(QRectF(px-w,  yopen,  w+w,  yclose-yopen))
                elif type == 1:
                    list[type].append(QRectF(px-w,  yclose,  w+w,  yopen-yclose))
                else:
                    list[type].append(QLineF(px-w,  yclose,  px+w,  yclose))
                        
        return list


class MainGraphGL(MainGraph):
    def __init__(self, data):
        super().__init__(data)
        
    def BuildBlock(self, block, dc):
        GL = dc.GL
        
        block.list_pass0 = GL.glGenLists(1)
        GL.glNewList(block.list_pass0, GL.GL_COMPILE)
        self.DrawCandleGraphGL(block, GL, 0)
        GL.glEndList()

        block.list_pass1 = GL.glGenLists(1)
        GL.glNewList(block.list_pass1, GL.GL_COMPILE)
        self.DrawCandleGraphGL(block, GL, 1)
        GL.glEndList()
        
        # set range
        block.ymin = min(self.data['low'][block.start_x : block.end_x])
        block.ymax = max(self.data['high'][block.start_x : block.end_x])  

    def DrawCandleGraphGL( self, block,  GL,  ipass):
        list = self.DrawCandleStickGraph( block.start_x,  block.end_x, ipass )

        if ipass == 0:
            # 红色
            self.DrawLinesGL(list[0], QColor(Qt.red), GL)
            # 绿色
            self.DrawLinesGL(list[1], QColor(Qt.darkGreen), GL)
            # 黑色
            self.DrawLinesGL(list[2], QColor(Qt.black), GL)
        else:
            # 红色
            self.DrawRectListGL(list[0], QColor(Qt.red), GL)
            # 绿色
            self.DrawRectListGL(list[1], QColor(Qt.darkGreen), GL)
            # 黑色
            self.DrawLinesGL(list[2], QColor(Qt.black), GL)
            
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
        
    def Draw(self, view, dc):
        GL = dc.GL
        
        x = view.rect.x()
        #y = 100
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
            GL.glCallList(block.list_pass0)
            if view.zoom > 2.8:
                GL.glCallList(block.list_pass1)

