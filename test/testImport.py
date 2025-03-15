import PyQt5.QtOpenGL as QtOpenGL

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

from PyQt5.QtGui import QTransform, QAbstractOpenGLFunctions
import math


class AxisBuilder:
    def __init__(self):
        pass
        
    def ComputeGirdSize(self,  scale,  view):
        (coefficien,  epower) = AxisBuilder.ToEnotation(scale)
        
        if coefficien > 3.5:
            coefficien = 5
        elif coefficien > 1.5:
            coefficien = 2
        else:
            coefficien = 1
            
        return coefficien * math.pow(10, epower)
        
    def ToEnotation( value ):
        if value > 10:
            for i in range(10):
                if value < 7.5:
                    return (value, i)
                value /= 10
        elif value < 1:
            for i in range(10):
                if value > 0.75:
                    return (value, -i)
                value *= 10
        else:
            return (value,  0)
        pass
        
t1 = AxisBuilder.ComputeGirdSize(0, 230,  None)
t2 = AxisBuilder.ComputeGirdSize(0, 56,  None)
t3 = AxisBuilder.ComputeGirdSize(0, 0.5,  None)
t4 = AxisBuilder.ComputeGirdSize(0, 120000,  None)

print('f')
