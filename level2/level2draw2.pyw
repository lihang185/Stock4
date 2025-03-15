import sys
from PyQt5.QtCore import Qt, QPoint,  QRectF,  QPointF,  QLineF
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import time

sys.path.append('C:/proj/Stock4')

from StockView.drawcandle import L2DayFile

            
def clip(v, min, max):
    v = v if v > min else min
    v = v if v < max else max
    return v

class L2:
    STICK_WIDTH = 20
    COLUMN_SPACE = 10
    COLUMN_WIDTH = int(STICK_WIDTH * 2 + COLUMN_SPACE)
    
    LEFT_MARGIN = 10
    
    HEIGHT_SCALE = 2

class Level2View(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tx = QPoint(0, 0)
        self.zoom = 1.0
        
        self.built = None

    def sortList(self, in_list,  is_buy):
        list_ = []
        for i, id in enumerate(in_list):
            pack = self.l2file.BuyOrderInfoById(id) if is_buy else self.l2file.SellOrderInfoById(id)
            order_id,  price,  volume,  act_vol,  finished, deal_count = pack 
            
            item = ( id, act_vol )
            list_.append(item)
            
        list_.sort( key=lambda item: item[1])
        return list_
            
    def filterByTime(self):
        LEN = self.l2file.DealCount()
        
        time_list = []
        
        last_hour = 0
        last_min = 0
        buy_list = []
        sell_list = []
        column_index = 0
        for i in range(LEN):
            (id, itime, is_buy, volume, price, buy_id, buy_flags, sell_id, sell_flags) = self.l2file.DealInfo(i)
            
            st_time = time.localtime(itime)
            
            if st_time.tm_hour != last_hour or st_time.tm_min != last_min:
                # 将之前数据保存到列表里
                if buy_list or sell_list:
                    # sort
                    buy_list_sorted = self.sortList(buy_list, True)
                    sell_list_sorted = self.sortList(sell_list, False)
                    
                    pack = (column_index, last_hour, last_min, buy_list_sorted, sell_list_sorted)
                    time_list.append(pack)
                    buy_list = []
                    sell_list = []
                    column_index+=1
                last_hour = st_time.tm_hour 
                last_min = st_time.tm_min
            
            # 买单的开始
            if buy_flags & 1:
                buy_list.append(buy_id)
                
            # 卖单的开始
            if sell_flags & 1:
                sell_list.append(sell_id)

        # sort
        buy_list_sorted = self.sortList(buy_list, True)
        sell_list_sorted = self.sortList(sell_list, False)
        pack = (column_index, last_hour, last_min, buy_list_sorted, sell_list_sorted)
        time_list.append(pack)      
        
        return time_list
        #self.time_list = time_list

    def createListByTime(self):
        
        list_ = []
        
        list_.append((9, 25))
        list_.append((9, 26))
        
        h=9; m = 30
        for i in range(0, 121):
            list_.append((h, m))
            m+=1
            if m == 60:
                h+=1
                m = 0
        
        list_.append((10, 31))
        
        h=13; m = 00
        for i in range(0, 121):
            list_.append((h, m))
            m+=1
            if m == 60:
                h+=1
                m = 0
                
        return list_
        
    def resortList(self,  T,  list_1):
        
        LEN = len(T)
        
        list_ = [None] * LEN
        
        for pack in list_1:
            column_index, hour, minute, buy_list, sell_list = pack
            
            # find
            found = False
            for i,  (h, m) in enumerate(T):
                if hour == h and minute == m:
                    list_[i] = pack
                    found = True
                    break
                    
            assert found,  "time not found"

        return list_

    def setData(self,  l2file):
        self.l2file = l2file
        
        self.TIME = self.createListByTime()
        list_1 = self.filterByTime()
        
        self.time_list = self.resortList(self.TIME, list_1)
        
    def findByTime(self, hour, minute):

        for i,  (h, m) in enumerate(self.TIME):
            if hour == h and minute == m:
                return i
        return -1
        
    def draw2(self, column_index, pack,  filterSize, painter ):
        ci, last_hour, last_min, buy_list, sell_list = pack
        
        # green
        x = int(column_index * L2.COLUMN_WIDTH + L2.LEFT_MARGIN)
        
        colors = (QtGui.QColor(220, 255, 220),  QtGui.QColor(0, 255, 0))
        
        if filterSize == 10:
            self.draw2_x10(sell_list, x,  colors, painter)
        else:
            self.draw2_detail(sell_list, x,  colors, painter)

        # red
        x += L2.STICK_WIDTH
        
        colors = (QtGui.QColor(255, 150, 150),  QtGui.QColor(255, 0, 0))

        if filterSize == 10:
            self.draw2_x10(buy_list, x,  colors, painter)
        else:
            self.draw2_detail(buy_list, x,  colors, painter)

        
    def draw2_detail(self, list_, start_x, colors, painter):

        y = 0
        for i, (id, vol) in enumerate(list_):
            h = int(vol/100)
            ey =  y+h
            
            color_idx = i % len(colors)
            color = colors[color_idx]
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            
            y1 = y // 10
            x1 = y % 10
            y2 = ey // 10
            x2 = ey % 10
            
            to = x2 if y2 == y1 else 10
            #for i in range(x1, to): used[i] = id
            
            # draw pre-block
            #if not x1 == 0:
            pre_block = QRectF(x1*2+start_x, y1*2, (to-x1)*2, 2)
            painter.drawRect(pre_block) 
            
            # draw block
            if y2 - y1 >= 2:
                block_ystart = y1 if x1 == 0 else y1+1
                block_yend = y2+1 if x2 == 0 else y2
                painter.drawRect(QRectF(start_x, block_ystart*2,  20,  (block_yend-block_ystart)*2))
                
            #def post-block
            if y2 > y1 and x2 != 0:
                painter.drawRect(QRectF(start_x, y2*2, x2*2, 2)) 
                
            pen = QtGui.QPen(Qt.black)
            pen.setCosmetic(True)
            painter.setPen(pen)
            
            # draw pre-block
            #if x1 != 0:
            painter.drawLine( QLineF(pre_block.x(),  y1*2, pre_block.x(),  y1*2+2) )
            painter.drawLine( QLineF(pre_block.x(), y1*2, pre_block.right(),  y1*2) )
            
            if y2 > y1:
                painter.drawLine( QLineF(start_x,  y1*2+2, pre_block.x(),  y1*2+2) )

            
            y = ey
            
        if y != 0:
            y1 = y // 10
            x1 = y % 10
            
            #final line
            painter.drawLine( QLineF(x1*2+start_x,  y1*2, x1*2+start_x,  y1*2+2) )
            painter.drawLine( QLineF(x1*2+start_x, y1*2, start_x + 20,  y1*2) )
            
            # top
            painter.drawLine( QLineF(start_x,  y1*2+2, start_x+20,  y1*2+2) )
            
            #left
            painter.drawLine( QLineF(start_x,  0, start_x,  y1*2+2) )
            #right
            painter.drawLine( QLineF(start_x+20,  0, start_x+20,  y1*2+2) )
            
    def draw2_x10(self, list_, start_x, colors, painter):
        
        y = 0
        for i, (id, vol) in enumerate(list_):
            h = int(vol/100)
            ey =  y+h
            
            color_idx = i % len(colors)
            color = colors[color_idx]
            painter.setBrush(color)
            #painter.setPen(Qt.NoPen)
            
            y1 = y // 10
            #x1 = y % 10
            y2 = ey // 10
            #x2 = ey % 10
            
            # draw block
            if y2 > y1:
                painter.drawRect(QRectF(start_x, y1*2,  20,  (y2-y1)*2))
                
            y = ey
        
    def draw1(self, pack, filterSize, painter ):
        column_index, last_hour, last_min, buy_list, sell_list = pack
        
        x = int(column_index * L2.COLUMN_WIDTH + L2.LEFT_MARGIN)
        
        colors = (QtGui.QColor(220, 255, 220),  QtGui.QColor(0, 255, 0))
        
        y=0
        last_y=0
        for i, (id, act_vol) in enumerate(sell_list):

            h = int(act_vol/100 * L2.HEIGHT_SCALE)

            if act_vol >= filterSize:
                if y != last_y:
                    painter.setBrush(Qt.black)
                    painter.drawRect(QRectF(x, last_y, L2.STICK_WIDTH, y-last_y))
                
                color_idx = i % len(colors)
                color = colors[color_idx]
                painter.setBrush(color)
                painter.drawRect(QRectF(x, y, L2.STICK_WIDTH, h))
                last_y = y+h
 
            y += h
        
        if y != last_y:
            painter.setBrush(Qt.black)
            painter.drawRect(QRectF(x, last_y, L2.STICK_WIDTH, y-last_y))

        colors = (QtGui.QColor(255, 150, 150),  QtGui.QColor(255, 0, 0))

        x += L2.STICK_WIDTH
        y=0
        last_y=0
        for i, (id, act_vol) in enumerate(buy_list):

            h = int(act_vol/100 * L2.HEIGHT_SCALE)
            
            if act_vol >= filterSize:
                if y != last_y:
                    painter.setBrush(Qt.black)
                    painter.drawRect(QRectF(x, last_y, L2.STICK_WIDTH, y-last_y))
                    
                color_idx = i % len(colors)
                color = colors[color_idx]
                painter.setBrush(color)
                painter.drawRect(QRectF(x, y, L2.STICK_WIDTH, h))
                last_y = y+h
 
            y += h
            
        if y != last_y:
            painter.setBrush(Qt.black)
            painter.drawRect(QRectF(x, last_y, L2.STICK_WIDTH, y-last_y))


    def drawRange(self, list_,  filterSize, painter ):
        
        pen = QtGui.QPen(Qt.black)
        pen.setCosmetic(True)
        painter.setPen(pen)
        #painter.setPen(Qt.NoPen)
        
        start_x = self.im.map(QPoint(0, 0)).x()
        end_x = self.im.map(QPoint(self.rect().width(), 0)).x()
        
        start_col = int( (start_x - L2.LEFT_MARGIN) / L2.COLUMN_WIDTH)
        start_col = clip(start_col,  0,  len(list_)+1)
        end_col = int( (end_x - L2.LEFT_MARGIN) / L2.COLUMN_WIDTH + 1)
        end_col = clip(end_col,  0,  len(list_)+1)
        
        for idx,  pack in enumerate(list_[start_col:end_col]):
            if pack:
                self.draw2(start_col+idx, pack, filterSize, painter)
            
    
    def buildDrawList(self, time_list ):
        
        # draw all
        drawlist = QtGui.QPicture()
        painter = QtGui.QPainter(drawlist)
        self.drawRange(time_list,  0, painter)
        painter.end()
        
        self.drawList1 = drawlist
        
        
        # draw > 1000
        drawlist = QtGui.QPicture()
        painter = QtGui.QPainter(drawlist)
        self.drawRange(time_list,  1000, painter)
        painter.end()
        
        self.drawList10 = drawlist
        
        # draw > 10000
        drawlist = QtGui.QPicture()
        painter = QtGui.QPainter(drawlist)
        self.drawRange(time_list,  10000, painter)
        painter.end()
        
        self.drawList100 = drawlist
        
    def drawAxis1(self,  column_index,  painter):
        # find time
        hour, minute = self.TIME[column_index]
        
        x = int(column_index * L2.COLUMN_WIDTH + L2.LEFT_MARGIN)
        
        pos = self.tm.map(QPoint(x, 0))

        painter.drawLine(pos.x(), pos.y() + 0,pos.x(), pos.y() + 5)
         
        painter.drawText(pos.x()+2, pos.y() + 18,"%d:%02d"%(hour, minute))
        
        
    
    def drawAxis(self,  painter):
        x = self.findByTime(9, 25)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(9, 30)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(10, 00)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(10, 30)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(11, 00)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(11, 29)
        self.drawAxis1(x, painter)


        x = self.findByTime(13, 00)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(13, 30)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(14, 00)
        self.drawAxis1(x, painter)
        
        x = self.findByTime(14, 30)
        self.drawAxis1(x, painter)

        x = self.findByTime(15, 00)
        self.drawAxis1(x, painter)

        
        
        
    def paintEvent(self, event=None):
        painter = QtGui.QPainter(self)
        
        # Transform
        transform=self.computeTransform()
        painter.setTransform(transform)
        
        # Build darwlist
        if self.built == None:
            #self.buildDrawList(self.time_list)
            self.built = True

        # Draw
        if self.zoom >= 1:
            self.drawRange(self.time_list, 1, painter)
        else:
            self.drawRange(self.time_list, 10, painter)

            
        # 2D text
        painter.resetTransform()
        self.drawAxis(painter)
        
        painter.drawText(10, 18,"scale: %f"%self.zoom)
        
        painter.end()
        painter = None
        
    def computeTransform(self):
        transform = QtGui.QTransform()
        transform.translate(self.tx.x(), self.tx.y())
        transform.translate(0, self.rect().height()-1)
        zoom_x = self.zoom if self.zoom > 0.2 else 0.2
        zoom_y = self.zoom
        transform.scale(zoom_x,  zoom_y)
        transform.scale(1, -1)
        self.tm = transform
        self.im = self.tm.inverted()[0]
        return transform

    def mouseMoveEvent(self, event):
        point=event.pos()
        diff = (point - self.dragpos)
        self.tx = self.dragstart_tx + diff
        
        # Refresh Screen
        self.repaint()
        
    def mousePressEvent(self,event):
        self.dragstart_tx = self.tx
        self.dragpos = event.pos()

    def wheelEvent(self, event):
        point = event.pos()
        delta = event.angleDelta().y()
        
        self.doZoom(point,  delta)
        
        # Refresh Screen
        self.repaint()

    def doZoom(self,  pos,  delta):
        # 第一步： 把鼠标位置 转换为 index
        p = self.im.map(pos)
        #X = self.layout.UnProjectX(sx)
        
        # 第二步： 缩放
        if delta < 0 :
            self.doZoomOut()
        else:
            self.doZoomIn()
        
        # 第三步 鼠标位置 - 屏幕坐标 = 开始位置
        self.computeTransform()
        diff = self.tm.map(p) - pos
        #diff.setY(0)
        self.tx -= diff
        
    def doZoomOut(self):
        if self.zoom >= 2:
            self.zoom = (float)(int(self.zoom) - 1)
        else:
            self.zoom -= self.zoom * 0.2
            
    def doZoomIn(self):
        if self.zoom >= 2:
            self.zoom = (float)(int(self.zoom) + 1)
        else:
            self.zoom += self.zoom * 0.2


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindows = QtWidgets.QMainWindow()
    view = Level2View()
    
    l2file = L2DayFile()
    
    ret = l2file.LoadFile("C:\\proj\\Stock4\\level2\\600083_0710")
    #ret = l2file.LoadFile("L:/level2/20191021/300071")

    if ret:
      view.setData(l2file)
    else:
      print('error')
  
    mainWindows.setCentralWidget(view)
    mainWindows.resize(1250, 587)
    mainWindows.show()
    app.exec_()   
    
