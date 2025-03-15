from PyQt5.QtCore import Qt, QLineF,  QRect,  QPointF
from PyQt5.QtGui import QPen, QBrush, QColor,  QPainter,  QTransform

from .AxisBuilder import *
from .PerformanceCounter import *

class EmptyLayout:
    def __init__(self):
        self.zoom = 1
        self.tx = -0
        self.empty = True
        
    def ProjectX(self,  x_index): return x_index
    def UnProjectX(self,  x_screen): return x_screen
    
    def ComputeLayout(self,  rect):
        self.rect = rect
        
    def Draw(self, dc):

        painter = dc.painter
        
        r = self.rect
        
        #######################
        # 绘制边框
        #######################    
        pen = QPen(Qt.black)
        painter.setPen(pen)
        painter.drawLine(r.left(), r.top(),  r.right(), r.top())
        painter.drawLine(r.left(), r.bottom(),  r.right(), r.bottom())

        painter.drawLine(r.left(), r.top(),  r.left(), r.bottom())
        painter.drawLine(r.right(), r.top(),  r.right(), r.bottom())
  
class ViewInfo:
    def __init__(self):
        self.tx = 0
        self.zoom = 0
        self.rect = None
        self.log_coord = False
        self.axis = None
        
    def Update(self, tx, zoom, rect):
        self.tx = tx
        self.zoom = zoom
        self.rect = rect
        
    def ProjectToScreenY(self, Y):
        scale = (Y - self.view_min)/ (self.view_max - self.view_min)
        SY = self.rect.y() + (1-scale) * self.rect.height()
        return SY
        
    def ProjectToScreenY_GL(self, Y):
        scale = (Y - self.view_min)/ (self.view_max - self.view_min)
        SY = (1-scale) * self.rect.height()
        return SY
        
    def UnProjectToY(self, SY):
        scale = (SY - self.rect.y()) / self.rect.height() 
        Y = (1-scale) *  (self.view_max - self.view_min) + self.view_min
        return Y
    
   
class SimpleLayout:
    LEFT_AXIS_WIDTH = 35
    RIGHT_AXIS_WIDTH =35
    TIME_AXIS_HEIGHT = 16      
    
    def __init__(self,  data):
        self.data = data
        self.LEN = data['data_length']
        
        self.zoom = 1
        self.tx = 0
        
        self.FONT_HEIGHT = 8
        
        self.draw_grid_3d = True
        self.log_coord = False
        self.margin = 20.0
        self.clipping = True
        self.line_width = 1.0
        self.empty = False
        
        self.rect = None
        self.main_graph = None
        self.is_drawing_overlay = False
        self.overlay_graph = None
        
        self.is_drawing_indicator = False
        self.indicator_graph = None
        
        self.pc = PerformanceCounter()
        self.is_drawing_pc = False
        
        self.logo = None
        self.LOGO_WIDTH = 50
        self.LOGO_HEIGHT = 50
        
        self.is_initialized = False


    def Build(self,  dc):
        if self.is_initialized:
            return
            
        self.view = ViewInfo()
        self.UpdateView(self.view, self.main_graph_rect )
        self.view.log_coord = self.log_coord
        self.main_graph.Build(self.view, dc)
        if self.overlay_graph1:
            self.overlay_graph1.Build(self.view, dc)
        if self.overlay_graph2:
            self.overlay_graph2.Build(self.view, dc)
            
        self.view2 = ViewInfo()
        self.UpdateView(self.view2, self.indicator_graph_rect )
        if self.indicator_graph:
            self.indicator_graph.Build(self.view2, dc)
        
        if self.logo:
            self.logo.Build(dc)

        self.time_axis = self.data['TimeAxis']
        
        # Finished
        self.is_initialized = True
    
    ############
    # 计算变换矩阵
    ############    
    def UpdateView(self,  view,  rect):
        view.tx = self.tx
        view.zoom = self.zoom
        view.rect = rect
        view.isClipping = self.clipping
        view.fullRect = self.window_rect
        
        #
        view.line_width = self.line_width
        
        ############
        # 计算x值范围
        ############
        view.view_start_x = (int)(view.tx / view.zoom)
        view.view_end_x = (int)((view.tx + view.rect.width()) / view.zoom)    

        view.start_x = view.view_start_x
        view.end_x = view.view_end_x

        LEN = self.main_graph.LEN
        if view.start_x < 0:
            view.start_x = 0
        if view.start_x > LEN-1:
            view.start_x = LEN-1
        if view.end_x < 0:
            view.end_x = 0
        if view.end_x > LEN-1:
            view.end_x = LEN-1
            
        return (view.start_x,  view.end_x)

    def ProjectX(self,  x_index):
        x_screen = (int)(float(x_index) * self.zoom - self.tx + self.graph_left )
        return x_screen
        
    
    def UnProjectX(self,  x_screen):
        index = (int)((float)(x_screen - self.graph_left + self.tx) / self.zoom)
        return index

    
    def BuildTransformation( self, view ):
        tm = QTransform()
        rect = view.rect

        tm.translate(rect.x(),  rect.y())
        tm.translate(-view.tx,  rect.height())
        tm.scale(view.zoom,  float(rect.height())/(view.view_max - view.view_min))
        tm.translate(0,  view.view_min)
        tm.scale(1,  -1)  
        
        view.tm = tm
        view.im = tm.inverted()[0]
        return tm

    ############
    # 绘图
    ############            
    def Draw(self, dc):

        #================
        # Main Graph
        #================
        self.Build(dc)
        
        # Start PC
        self.pc.start(4)
        
        dc.painter.beginNativePainting()
        #================
        # Main Graph
        #================
        self.pc.start(0)
        self.UpdateView(self.view, self.main_graph_rect )
        # 计算Y轴范围，以此计算矩阵
        self.main_graph.margin = self.margin
        self.main_graph.ComputeRange(self.view)

        self.main_graph.Draw(self.view,  dc)
        # Grid
        if self.log_coord:
            axisgen = AxisBuilderLogCoord(self.view, 8 )
            self.view.axis = axisgen.Build()
        else:
            axisgen = AxisBuilder(self.view, 8)
            self.view.axis = axisgen.Build()
        if self.is_draw_grid:
            if self.draw_grid_3d:
                self.main_graph.DrawGrid(self.view, dc)
            else:
                self.main_graph.SetupTransform2D(self.view,  dc)
        self.pc.end(0)

        #================
        # Overlay Graph
        #================ 
        self.pc.start(1)
        if self.is_drawing_overlay1:
            self.overlay_graph1.Draw(self.view,  dc)
        if self.is_drawing_overlay2:
            self.overlay_graph2.Draw(self.view,  dc)
        self.pc.end(1)
        
        #================
        # Indicator Graph
        #================
        self.pc.start(2)
        self.UpdateView(self.view2, self.indicator_graph_rect)
        if self.is_drawing_indicator and self.is_drawing_bottom :
            # 计算Y轴范围，以此计算矩阵
            self.indicator_graph.ComputeRange(self.view2)
            self.indicator_graph.Draw(self.view2,  dc)
            # Grid
            axisgen = AxisBuilder(self.view2, 8)
            self.view2.axis = axisgen.Build()
            if self.is_draw_grid:
                if self.draw_grid_3d:
                    self.indicator_graph.DrawGrid(self.view2, dc)
                else:
                    self.indicator_graph.SetupTransform2D(self.view2,  dc)
        self.pc.end(2)
        
        #================
        # 3D Logo
        #================
        self.pc.start(5)       
        if self.draw_grid_3d and self.logo: 
            view3 = ViewInfo()
            self.UpdateView(view3, self.logo_rect )
            self.logo.yRot = self.tx*10 + 520
            #self.logo.zRot = math.pow(self.zoom, 1.2)*500
            self.logo.Draw(view3, dc)
        self.pc.end(5)        
        
        dc.painter.endNativePainting()

        #================
        #  2D 
        #================
        self.pc.start(3)        
        self.Draw2D(dc)
        self.pc.end(3) 

        self.pc.end(4)

    def Draw2D(self,  dc):
        painter = dc.painter
        #================
        # 后面部分是绘制2D图形
        # 需要精确到像素点上
        # 一个小Hack可解决OpenGL
        # 绘制二位图像浮点数不
        # 能精确到像素的问题
        #================
        painter.resetTransform()
        painter.translate(0.5, 0.5)

        #================
        # Axis Scale
        #================
        if self.is_drawing_rightaxis:
            self.DrawAxis(self.view.axis, painter)
        if self.is_draw_grid and not self.draw_grid_3d:
            self.DrawGrid2D(self.view.axis, painter)

        if self.is_drawing_indicator and self.is_drawing_bottom:
            self.DrawAxis(self.view2.axis, painter)
            if self.is_draw_grid and not self.draw_grid_3d:
                self.DrawGrid2D(self.view2.axis, painter)
        
        # time axis
        if self.is_drawing_bottom:
            self.DrawTimeAxis(painter)

        #================
        #  Frame Border
        #================
        self.DrawLayoutFrame(painter)
 

    def DrawGrid2D(self,  list,  painter):
        # Draw Gird
        pen1 = QPen(Qt.gray)
        pen1.setCosmetic(True)
        pen1.setStyle(Qt.DotLine)
        pen2 = QPen(Qt.red)
        pen2.setCosmetic(True)
        pen2.setStyle(Qt.DotLine)
        for (y,  ylog, py,  type) in list:
            if type == 0:
                painter.setPen(pen1)
                painter.drawLine( self.graph_left,  py,  self.graph_right,  py)
            else:
                painter.setPen(pen2)
                painter.drawLine( self.graph_left,  py,  self.graph_right,  py)
  
    def DrawAxis(self, list, painter):
        # Draw Axis
        self.SetFont(Qt.black, painter)

        for (y,  ylog, py,  type) in list:
            if type == 0 or type == 1:
                py = int(py)
                painter.drawLine( self.graph_right,  py,  self.graph_right+3,  py)
                if y > 999:
                    text = "%4.0f"%(y)
                elif y > 99:
                    text = "%3.1f"%(y)
                else:
                    text = "%2.2f"%(y)

                painter.drawText(self.graph_right+5, py+4,text)
                
    def DrawTimeAxis(self, painter):
        self.SetFont(Qt.black, painter)
        
        list = self.time_axis.year_list
        for x, idate in list:
            px = self.ProjectX(x)
            if px < self.graph_left or px > self.graph_right-25:
                continue
            
            painter.drawLine(px, self.timeaxis_top, px, self.timeaxis_top+SimpleLayout.TIME_AXIS_HEIGHT)
            
            if self.zoom > 0.13:
                FromIDate = type(self.time_axis).FromIDate
                year, month, day = FromIDate(idate)
                painter.drawText(px+3, self.timeaxis_top + self.TIME_AXIS_HEIGHT-3,"%4d"%(year))
    
    def SetFont(self, color, painter):
        font=painter.font()
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(color)
        
    ############
    # 计算布局
    ############        
    def ComputeLayout(self,  rect  ):
        self.rect = rect
        self.window_rect = rect
        
        LEFT = self.rect.left()
        RIGHT = self.rect.right()
        TOP = self.rect.top()
        BOTTOM = self.rect.bottom()
        
        WIDTH = self.rect.width()
        HEIGHT = self.rect.height()
        
        self.is_drawing_leftaxis = True if  WIDTH >= 300 else False
        self.is_drawing_rightaxis = True if WIDTH >= 300 else False
        self.is_drawing_bottom = True if HEIGHT  >= 150 else False
        #self.is_drawing_indicator = True if self.indicator_graph != None else False
        
        # Width
        self.graph_left = LEFT + SimpleLayout.LEFT_AXIS_WIDTH if self.is_drawing_leftaxis else LEFT
        self.graph_right = RIGHT - SimpleLayout.RIGHT_AXIS_WIDTH if self.is_drawing_rightaxis else RIGHT
        self.graph_width = self.graph_right - self.graph_left
        #self.graph_width = WIDTH - self.graph_left - (SimpleLayout.LEFT_AXIS_WIDTH if self.is_drawing_leftaxis else 0)
        
        # Height
        totalHeight =  HEIGHT - SimpleLayout.TIME_AXIS_HEIGHT if self.is_drawing_bottom else HEIGHT
        indicator_height = int(totalHeight * 0.3)

        # MainGraph
        self.main_graph_height = totalHeight - indicator_height if (self.is_drawing_indicator and self.is_drawing_bottom) else totalHeight
        # IndicatorGraph
        self.indicator_top = self.main_graph_height
        self.indicator_height = indicator_height
        
        # Build Rect for MainGraph and IndicatorGraph
        self.main_graph_rect = QRect(self.graph_left,  TOP+15,  self.graph_width,  self.main_graph_height-15)
        self.indicator_graph_rect = QRect(self.graph_left,  self.indicator_top+10,  self.graph_width,  self.indicator_height-10)
        
        self.timeaxis_top = BOTTOM - SimpleLayout.TIME_AXIS_HEIGHT
        
        # 3D logo
        #LOGO_WIDTH = 50
        #LOGO_HEIGHT = 50
        self.logo_rect = QRect( self.graph_left,  self.main_graph_rect.bottom()-self.LOGO_HEIGHT, self.LOGO_WIDTH, self.LOGO_HEIGHT)
        
        # PC
        PC_WIDTH = 120
        PC_HEIGHT = 100
        self.pc_rect = QRect( self.graph_right-PC_WIDTH,  self.main_graph_rect.bottom()-PC_HEIGHT, PC_WIDTH, PC_HEIGHT)
        
    
    ############
    # 绘制布局边框
    ############
    def DrawLayoutFrame(self, painter):
        r = self.rect
        WIDTH = self.rect.width()
        HEIGHT = self.rect.height()
        
        #######################
        # 绘制边框
        #######################    
        pen = QPen(Qt.black)
        painter.setPen(pen)
        painter.drawLine(r.left(), r.top(),  r.right(), r.top())
        painter.drawLine(r.left(), r.bottom(),  r.right(), r.bottom())

        painter.drawLine(r.left(), r.top(),  r.left(), r.bottom())
        painter.drawLine(r.right(), r.top(),  r.right(), r.bottom())

        # title
        self.SetFont(Qt.black, painter)
        painter.drawText(self.graph_left+5,  r.top() + self.FONT_HEIGHT + 4,"%s"%(self.data['code']))
        #painter.drawLine( 0,  15,  WIDTH, 15)
        # 左边轴边框 
        if self.is_drawing_leftaxis:
            painter.drawLine( self.graph_left-1,  r.top(),  self.graph_left-1,  r.bottom())
        # 右边轴边框
        if self.is_drawing_rightaxis:
            painter.drawLine( self.graph_right,  r.top(),  self.graph_right,  r.bottom())
            
        # 如果窗口高度足够，就绘制底部组件
        if self.is_drawing_bottom:
            # Indicator1
            if self.is_drawing_indicator:
                painter.drawLine( r.left(),  self.indicator_top,  r.right(),  self.indicator_top)
            # 底部时间轴
            painter.drawLine( r.left(),  self.timeaxis_top,  r.right(),  self.timeaxis_top)

    ############
    # 显示性能数据
    ############
    def DrawPC(self,  painter):
        if not self.is_drawing_bottom:
            return
        painter.translate(self.pc_rect.x(),  self.pc_rect.y())
        self.pc.rect = self.pc_rect
        self.pc.Draw(painter)
        painter.resetTransform()

    def END(self):
        pass
