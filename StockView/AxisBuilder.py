
from PyQt5.QtCore import QPointF
import math

class AxisBuilderLogCoord:
    def __init__(self,  view, fh):
        self.view = view
        self.log11 = math.log(1.1)

        self.org_min = math.pow(1.1, view.view_min)
        self.org_max = math.pow(1.1, view.view_max)

        self.font_height = fh / 2 + 4
        self.height = view.rect.height()
        
        self.list = []
        
    def Add(self,  y,  type):
        if y < self.org_min or y > self.org_max:
            return
        # project to py
        y_log = math.log(y)/self.log11
        #py = self.tm.map(QPointF(0, y_log)).y()
        py = self.view.ProjectToScreenY(y_log)
        if py < self.font_height or py >= self.height - self.font_height:
            return
            
        self.list.append((y, y_log,  py, type))
            

    def Build2(self):
        Q3 = math.pow(10, 1/3)
        
        (a, n) = AxisBuilderLogCoord.ToEnotation(self.org_min)
        
        a = int(a)
        b = 0
        while True:
            y = (a+b*0.1) * math.pow(10, n)
            
            if y > self.org_max:
                break
            
            if a==1 and b==0:
                self.Add(y,  1)
            else:
                self.Add(y,  0)
           

            ###########
            # Next Step
            a+=1
            
            ###########
            # Next Level
            if a==10:
                a=1
                n+=1
                self.Add(Q3      * math.pow(10, n),  2)
                self.Add(Q3*Q3 * math.pow(10, n),  2)
        
        return self.list

    def Build(self):
        Q3 = math.pow(10, 1/3)
        
        (a, n) = AxisBuilderLogCoord.ToEnotation(self.org_min)
        
        a = int(a)
        b = 0
        while True:
            y = (a+b*0.1) * math.pow(10, n)
            
            if y > self.org_max:
                break
            
            if a==1 and b==0:
                self.Add(y,  1)
            else:
                self.Add(y,  0)
            
            # 2.1544
            if a==2:
                self.Add(Q3      * math.pow(10, n),  2)
            # 4.3088
            if a==4:
                self.Add(Q3*Q3 * math.pow(10, n),  2)           

            ###########
            # Next Step
            if a==1:
                # 1.0 1.2 1.4 1.6.1.8
                b+=2
                if b==10:
                    a=2
                    b=0
            else:
                # 2 3 4 5 6 7 8 9
                a+=1
            
            ###########
            # Next Level
            if a==10:
                a=1
                n+=1

        return self.list

    def ToEnotation( value ):
        if value > 10:
            for i in range(30):
                if value < 10:
                    return (value, i)
                value /= 10
        elif value < 1:
            for i in range(30):
                if value >= 1:
                    return (value, -i)
                value *= 10

        return (value,  0)


class AxisBuilder:
    GIRD_HEIGHT = 50
    
    def __init__(self,  view, fh):
        self.view = view
        self.view_min = view.view_min
        self.view_max = view.view_max
        
        self.font_height = fh / 2 + 4
        self.rect_top = view.rect.y()
        self.rect_bottom = self.rect_top + view.rect.height()
        
        self.list = []
        
    def Add(self,  y):
        #py = self.tm.map(QPointF(0, y)).y()
        py = self.view.ProjectToScreenY(y)
        if py < self.rect_top + self.font_height or py >= self.rect_bottom - self.font_height:
            return
        self.list.append((y, y, py,  0))
  
    def Build(self):
        
        # 屏幕坐标上2个点映射到Y轴上的值
        #v = self.im.map(QPointF(0, 0))
        v = self.view.UnProjectToY(0)
        #v2 = self.im.map(QPointF(0, AxisBuilder.GIRD_HEIGHT))
        v2 = self.view.UnProjectToY(AxisBuilder.GIRD_HEIGHT)
        
        # 2点的差值就是坐标轴上刻度值得间隔
        diff = abs(v2 - v)
        interval = AxisBuilder.ComputeGirdSize(diff)
        
        # 创建刻度值列表 以及屏幕Y坐标
        y = 0
        while y < self.view_max:
            
            if y > self.view_min:
                self.Add(y)
                
            y += interval
            
        y = -interval
        while y > self.view_min:
            
            if y < self.view_max:
                self.Add(y)
                
            y += -interval    
            
        return self.list;
   
    def ComputeGirdSize(scale):
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
                if value >= 0.75:
                    return (value, -i)
                value *= 10
        else:
            return (value,  0)



