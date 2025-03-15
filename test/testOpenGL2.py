import sys
import math
 
from PyQt5.QtCore import (QPoint, QPointF, QLineF,  QRect, QRectF, QSize, Qt, QTime,
        QTimer)
from PyQt5.QtGui import (QBrush, QColor, QFontMetrics, QImage,
        QOpenGLVersionProfile, QPainter, QRadialGradient, QSurfaceFormat)
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
 
 
 
class GLWidget(QOpenGLWidget):
 
    def __init__(self, parent):
        super(GLWidget, self).__init__( parent)
 
 
    def initializeGL(self):
        version_profile = QOpenGLVersionProfile()
        version_profile.setVersion(2, 0)
        self.gl = self.context().versionFunctions(version_profile)
        self.gl.initializeOpenGLFunctions()

        self.gl.glClearColor(0.98, 0.98, 0.98, 1.0)
 
    def resizeGL(self, w, h):
        #self.gl.glViewport(0, 0, w, h)
        pass
        
    def drawFrameTest(self,  painter):
        w = self.width()
        h = self.height()
        
        painter.setPen(Qt.blue)
        painter.drawLine( QLineF(0,  -0.002,  w-1, -0.002))
        painter.drawLine( QLineF(0.00197,  0,  0.00197,  h-1))
        painter.drawLine( 0,  h-1+0.9,  w-1,  h-1+0.9)
        painter.drawLine( QLineF(w-1+0.1,  0,  w-1+0.1,  h-1))
        # X阈值 > 0.00197 ( 0.00196-0.00197 )
        # Y阈值 > -0.00197 ( -0.00196-0.00197 )       
        
    def paintEvent2(self,  event):
        painter = QPainter(self)
        
        w = self.width()
        h = self.height()
        
        painter.translate(0.5,  0.5)
        
        painter.setPen(Qt.blue)
        painter.drawLine( QLineF(0,  -0.1,  w-1, -0.1))
        painter.drawLine( QLineF(0,  0,  0,  h-1))
        painter.drawLine( QLineF(0,  h-1,  w-1,  h-1))
        painter.drawLine( QLineF(w-1,  0,  w-1,  h-1))
        # X阈值 > 0.00197 ( 0.00196-0.00197 )
        # Y阈值 > -0.00197 ( -0.00196-0.00197 )        
        
        painter.end()
        
    def paintEvent(self,  event):
        self.makeCurrent()
        
        w = self.width()
        h = self.height()
        
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT);
        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glOrtho( -0.5, w-1+0.5, h-1+0.5, -0.5, 0, 1)
        self.gl.glViewport(0, 0, w, h)

        self.gl.glColor3f(1.0, 0.0, 0.0);
        #画分割线，分成四个视区  
        self.gl.glBegin(self.gl.GL_LINES);
        
        # top
        self.gl.glVertex2d(0, 0);
        self.gl.glVertex2d(w, 0);
        # bottm
        self.gl.glVertex2d(0, h-1);
        self.gl.glVertex2d(w, h-1);        
        #left
        self.gl.glVertex2d(0, 0);
        self.gl.glVertex2d(0, h);
        #right
        self.gl.glVertex2d(w-1, 0);
        self.gl.glVertex2d(w-1, h);
        self.gl.glEnd();
         
        #定义在左下角的区域  
        self.gl.glColor3f(0.0, 1.0, 0.0);
        self.gl.glBegin(self.gl.GL_POLYGON);
        self.gl.glVertex2f(10, 10);
        self.gl.glVertex2f(10, 100);
        self.gl.glVertex2f(100,100 );
        self.gl.glVertex2f(100, 10);
        self.gl.glEnd();

        self.gl.glFlush()
        
        painter = QPainter(self)
        
        painter.setPen(Qt.blue)
        painter.drawLine( 0,  2,  w,  2)
        painter.drawLine( 2,  0,  2,  h)
        
        painter.end()

 
if __name__ == '__main__':
 
    app = QApplication(sys.argv)
 
    widget = GLWidget(None)
    widget.resize(640, 480)
    widget.show()
 
    sys.exit(app.exec_())
 
