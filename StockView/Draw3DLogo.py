from PyQt5.QtGui import QColor

import math

class Draw3DLogo:
    def __init__(self):
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)

    def Build(self, dc):
        if not dc.isOpenGLValid:
            return
        self.gl = dc.GL
        self.object = self.makeObject()

    def Draw(self, view, dc):
        if not dc.isOpenGLValid:
            return
            
        self.gl = dc.GL

        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        self.gl.glPushMatrix()

        self.gl.glShadeModel(self.gl.GL_SMOOTH)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        #self.gl.glEnable(self.gl.GL_CULL_FACE)
        self.gl.glEnable(self.gl.GL_LIGHTING)
        self.gl.glEnable(self.gl.GL_LIGHT0)
        #self.gl.glEnable(self.gl.GL_MULTISAMPLE)
        self.gl.glLightfv(self.gl.GL_LIGHT0, self.gl.GL_POSITION,
                (0.5, 5.0, 7.0, 1.0))

        self.setupViewport(view)

        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        
        red = view.zoom if view.zoom < 1.0 else 1.0
        green = 1.0 - red
        self.gl.glMaterialfv(self.gl.GL_FRONT, self.gl.GL_DIFFUSE,
                (red,green,0, 1.0) )
        
        self.gl.glCallList(self.object)
        
        self.gl.glDisable(self.gl.GL_DEPTH_TEST)
        #self.gl.glDisable(self.gl.GL_CULL_FACE)
        self.gl.glDisable(self.gl.GL_LIGHTING)
        self.gl.glDisable(self.gl.GL_LIGHT0)

        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        self.gl.glPopMatrix()
        
    def setupViewport(self,  view):
        x = view.rect.x()
        y = view.fullRect.height() - view.rect.y() - view.rect.height()
        w = view.rect.width()
        h = view.rect.height()

        self.gl.glViewport(x, y, w, h)        
        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        
    def SetupTransform2D(view, dc):
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
        
    def makeObject(self):
        list = self.gl.glGenLists(1)
        self.gl.glNewList(list, self.gl.GL_COMPILE)

        self.gl.glEnable(self.gl.GL_NORMALIZE)
        self.gl.glBegin(self.gl.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * math.pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * math.pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        self.gl.glEnd()

        self.gl.glEndList()
        return list

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.gl.glNormal3d(0.0, 0.0, -1.0)
        self.gl.glVertex3d(x1, y1, -0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x3, y3, -0.05)
        self.gl.glVertex3d(x4, y4, -0.05)

        self.gl.glNormal3d(0.0, 0.0, 1.0)
        self.gl.glVertex3d(x4, y4, +0.05)
        self.gl.glVertex3d(x3, y3, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.setColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        self.gl.glNormal3d((x1 + x2)/2.0, (y1 + y2)/2.0, 0.0)
        self.gl.glVertex3d(x1, y1, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x1, y1, -0.05)

    def setColor(self, c):
        self.gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())
