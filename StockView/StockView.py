from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .config import *

from .Layout import EmptyLayout


class DrawContext:
    def __init__(self):
        self.painter = None
        self.isOpenGLValid = False
        self.GL = None


class StockViewBase():
        
    def __init__(self, parent=None):
        self.dragstart_tx = 0
        self.dragstart_x = 0

        self.layout = EmptyLayout()
        
    def SetLayout(self,  layout):
        # 赋值指令使旧的对象不再被
        # 引用（引用计数为零）
        # 这可直接触发对象进入销毁
        # 状态并调用对象的析构函数
        self.layout = None

        #然后重新赋值
        self.layout = layout
        
    def sizeHint(self):
        return QSize(1400, 600);
  
    def mininumSizeHint(self):
        return QSize(300, 200);

    def mouseMoveEvent(self, event):
        point=event.pos()
        diff = -(point.x() - self.dragstart_x)
        self.layout.tx = self.dragstart_tx + diff
        
        # Refresh Screen
        self.repaint()
        
    def mousePressEvent(self,event):
        self.dragstart_tx = self.layout.tx
        self.dragstart_x = event.pos().x()
        
    def wheelEvent(self, event):
        point = event.pos()
        delta = event.angleDelta().y()
        
        self.DoZoom(point.x(),  delta)
        
        # Refresh Screen
        self.repaint()

    def DoZoom(self,  sx,  delta):
        # 第一步： 把鼠标位置 转换为 index
        X = self.layout.UnProjectX(sx)
        
        # 第二步： 缩放
        if delta < 0 :
            self.DoZoomOut()
        else:
            self.DoZoomIn()
        
        # 第三步 鼠标位置 - 屏幕坐标 = 开始位置
        diff = self.layout.ProjectX(X) - sx
        self.layout.tx += diff
        
    def DoZoomOut(self):
        if self.layout.zoom >= 2:
            self.layout.zoom = (float)(int(self.layout.zoom) - 1)
        else:
            self.layout.zoom -= self.layout.zoom * 0.2
            
    def DoZoomIn(self):
        if self.layout.zoom >= 2:
            self.layout.zoom = (float)(int(self.layout.zoom) + 1)
        else:
            self.layout.zoom += self.layout.zoom * 0.2

#class StockView(QOpenGLWidget):
class StockViewNormal(QWidget, StockViewBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Background
        palette = QPalette(self.palette())
        palette.setColor(QPalette.Background,  colorSchemes['background'])
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        

    def paintEvent(self, event=None):
        dc = DrawContext()
        dc.painter = QPainter(self)
       
        if self.layout.empty:
            self.layout.ComputeLayout(self.rect())
            self.layout.Draw(dc)
            return
        
    
        ##############
        # 主循环
        ##############        
        self.layout.ComputeLayout(self.rect())
        self.layout.Draw(dc)

        ##############
        # PerformanceCounter
        ##############
        if self.layout.is_drawing_pc:
            self.layout.DrawPC(dc.painter)
            
        # 必须释放painter
        dc.painter.end()
        dc = None
    
class StockViewOpenGL(QOpenGLWidget, StockViewBase   ):
    def __init__(self, parent):
        super(StockViewOpenGL, self).__init__( parent)
        self.setAutoFillBackground(False)

    def initializeGL(self):
        version_profile = QOpenGLVersionProfile()
        version_profile.setVersion(2, 0)
        self.gl = self.context().versionFunctions(version_profile)
        self.gl.initializeOpenGLFunctions()

    def paintEvent(self, event=None):
        self.makeCurrent()

        dc = DrawContext()
        dc.GL = self.gl
        dc.isOpenGLValid = True
        dc.painter = QPainter(self)

        self.gl.glClearColor(0.98, 0.98, 0.98, 1.0)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)

        if self.layout.empty:
            dc.painter.translate(0.5, 0.5)
            self.layout.ComputeLayout(self.rect())
            self.layout.Draw(dc)
            return

        
        # 大概QPainter中关闭了反走样
        # 如果在QPainter初始化之前调用
        # 反走样就不会工作
        self.gl.glEnable(self.gl.GL_MULTISAMPLE)        

        ##############
        # 主循环
        ##############        
        #dc.painter.translate(0.5, 0.5)
        self.layout.ComputeLayout(self.rect())
        self.layout.Draw(dc)

        ##############
        # PerformanceCounter
        ##############
        if self.layout.is_drawing_pc:
            self.layout.DrawPC(dc.painter)
            
        # 必须释放painter
        dc.painter.end()
        dc = None
