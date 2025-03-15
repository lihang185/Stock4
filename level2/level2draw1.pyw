import sys
from PyQt5.QtCore import Qt, QPoint,  QRectF
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import time

sys.path.append('C:/proj/Stock4')
import warnings
try:
    from l2file import L2DayFile
except ImportError as v:
    warnings.warn( "Import L2DayFile(l2file.pyd) extension failed.", RuntimeWarning)
    print(v)
    raise
    

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
            
        #list_.sort( key=lambda item: item[1])
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

        self.time_list = time_list
        
    def setData(self,  l2file):
        self.l2file = l2file
        self.filterByTime()
        
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
        
        for pack in list_:
            self.draw1(pack, filterSize, painter)
            
    
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
        
        
    def paintEvent(self, event=None):
        painter = QtGui.QPainter(self)
        
        # Transform
        transform=self.computeTransform()
        painter.setTransform(transform)
        
        # Build darwlist
        if self.built == None:
            self.buildDrawList(self.time_list)
            self.built = True

        # Draw
        if self.zoom > 0.5:
            painter.drawPicture(0, 0, self.drawList1)
        elif self.zoom > 0.05:
            painter.drawPicture(0, 0, self.drawList10)
        else:
            painter.drawPicture(0, 0, self.drawList100)
        #self.drawRange(self.time_list, painter)

            
        # 2D text
        painter.resetTransform()
        painter.drawText(10, 18,"scale: %f"%self.zoom)
        
        painter.end()
        painter = None
        
    def computeTransform(self):
        transform = QtGui.QTransform()
        transform.translate(self.tx.x(), self.tx.y())
        transform.translate(0, self.rect().height()-1)
        zoom_x = self.zoom if self.zoom > 0.2 else 0.2
        transform.scale(zoom_x,  self.zoom)
        transform.scale(1, -1)
        self.tm = transform
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
        im = self.tm.inverted()[0]
        p = im.map(pos)
        #X = self.layout.UnProjectX(sx)
        
        # 第二步： 缩放
        if delta < 0 :
            self.doZoomOut()
        else:
            self.doZoomIn()
        
        # 第三步 鼠标位置 - 屏幕坐标 = 开始位置
        tm = self.computeTransform()
        diff = tm.map(p) - pos
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
    #ret = l2file.LoadFile("C:/proj/Stock4/test/20190325/000016")
    ret = l2file.LoadFile("C:/proj/Stock4/test/000058")
    

    if ret:
      view.setData(l2file)
    else:
      print('error')
  
    mainWindows.setCentralWidget(view)
    mainWindows.resize(1250, 587)
    mainWindows.show()
    app.exec_()   
    
