from PyQt5.QtCore import Qt, QLineF,  QRect,  QPointF
from PyQt5.QtGui import QPen, QBrush, QColor,  QPainter,  QTransform
from StockView import *


from .Layout import *

class GridLayout:
    def __init__(self, columns, rows):
        self.zoom = 1
        self.tx = -0
        self.empty = False
        
        self.is_drawing_pc = False
        
        self.columns = columns
        self.rows = rows
       
        counts = int(columns * rows)
        list_ = []
        for i in range(counts):
            view = EmptyLayout()
            list_.append(view)
            
        self.grid = list_
        
        self.pc = PerformanceCounter()
        self.is_drawing_pc = True
        
       

        
    def SetDataCenter(self, factory):
        self.factory = factory

    def SetMainView(self, xi, yi):
        index = int(yi * self.columns + xi)
        self.main_view = self.grid[index]
        
    def GetView(self,  xi, yi):
        index = int(yi * self.columns + xi)
        return self.grid[index]
        
    def CreateView(self, xi, yi, stock_data):
      
        # Layout 
        layout = SimpleLayout(stock_data)
        # Main
        layout.main_graph = MainGraph(stock_data)
        # Overlay 1
        layout.is_drawing_overlay1 = True
        layout.overlay_graph1 =  GraphEngine(MAIndicator(stock_data))
        layout.is_drawing_overlay2 = False
        layout.overlay_graph2 = None
        layout.indicator_graph = False
        layout.is_drawing_pc = False
        layout.is_draw_grid = True
        layout.draw_grid_3d = True
        layout.logo = None
        
        index = int(yi * self.columns + xi)
        self.grid[index] = layout
        
    def ProjectX(self,  x_index):
        graph_left = self.main_view.graph_left if self.main_view else 0
        x_screen = (int)(float(x_index) * self.zoom - self.tx + graph_left )
        return x_screen
        
    
    def UnProjectX(self,  x_screen):
        graph_left = self.main_view.graph_left if self.main_view else 0
        index = (int)((float)(x_screen - graph_left + self.tx) / self.zoom)
        return index

    def ComputeLayout(self,  rect):
        self.rect = rect
        WIDTH = self.rect.width()
        HEIGHT = self.rect.height()        
        
        self.grid_width = int(WIDTH / self.columns)
        self.grid_height = int(HEIGHT / self.rows)
        
        for xi in range(self.columns):
            for yi in range(self.rows):
                
                x = self.grid_width * xi
                y = self.grid_height * yi
                
                view_rect = QRect(x, y, self.grid_width, self.grid_height)
                index = int(yi * self.columns + xi)
                view = self.grid[index]
                view.zoom = self.zoom
                view.tx = self.tx
                view.ComputeLayout(view_rect)
                view.window_rect = rect


        # PC
        PC_WIDTH = 120
        PC_HEIGHT = 100
        self.pc_rect = QRect( self.main_view.graph_right-PC_WIDTH,  self.main_view.main_graph_height-PC_HEIGHT, PC_WIDTH, PC_HEIGHT)
       

    def Draw(self, dc):
        self.pc.start(4)

        self.pc.start(0)
        self.main_view.Draw(dc)
        self.pc.end(0)

        
        for view in self.grid:
            if view == self.main_view:
                continue
                
            view.Draw(dc)
            
            ##############
            # PerformanceCounter
            ##############
            #if view.is_drawing_pc:
            #    view.DrawPC(dc.painter)
                
        self.pc.end(4)
        
   
        if self.is_drawing_pc:
            self.DrawPC(dc.painter)
            

    ############
    # 显示性能数据
    ############
    def DrawPC(self,  painter):
        painter.translate(self.pc_rect.x(),  self.pc_rect.y())
        self.pc.rect = self.pc_rect
        self.pc.Draw(painter)
        painter.resetTransform()
