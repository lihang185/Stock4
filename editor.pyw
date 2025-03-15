from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QSurfaceFormat

import StockView
StockView.g_Enable_OpenGL()


import Ui_editor

from StockView import MainGraph,  GraphEngine,  SimpleLayout,  LineSegmentData,  LineSegmentGraph
from StockView.BaseIndicators import MACD, KDJ,  VOLIndicator, MAIndicator
from StockView.Draw3DLogo import Draw3DLogo

from tdx import DataCenter



class EditorMain(QtWidgets.QMainWindow, Ui_editor.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lineEdit.setText('sh600036')
        self.empty = True
        
    def loadButtonClicked(self,  e):
        stockid = self.lineEdit.text()
        # 复权
        use_gbbq = self.checkBox_gbbq.isChecked()
        # 对数坐标
        log_coord = self.checkBox_logcoord.isChecked()
        
        # 斜率修正
        slope = self.doubleSpinBox_slope.value()
        
        # 主图边缘
        margin = self.doubleSpinBox_margin.value()
 
        if not stockid:
            return

        ###########
        # 股票数据
        ###########
        self.dm = DataCenter()
        if not self.dm.LoadStockData(stockid,  use_gbbq, slope):
            return

        stock_data = self.dm.data
        

        ###########
        # GUI 显示指标选项
        ###########
        overlay1 = None
        if self.radioButton_MA.isChecked():
            overlay1 = GraphEngine(MAIndicator(stock_data))
        elif self.radioButton_bookvalue.isChecked():
            fin_data = self.dm.LoadFromCSV('finance_db', 'book_value')
            ind = LineSegmentData(fin_data, stock_data)
            overlay1 = LineSegmentGraph(ind)
        # is drawing
        draw_overlay_graph1 = self.checkBox_overlay1.isChecked() and overlay1 != None
        
        overlay2 = GraphEngine(MAIndicator(stock_data))
        draw_overlay_graph2 = self.checkBox_overlay2.isChecked()

        
        # indicator graph           
        indicator1 = None
        if self.radioButton_MACD.isChecked():
            indicator1 = GraphEngine(MACD(stock_data))
        elif self.radioButton_KDJ.isChecked():
            indicator1 = GraphEngine(KDJ(stock_data))
        elif self.radioButton_VOL.isChecked():
            indicator1 = GraphEngine(VOLIndicator(stock_data))
        # is drawing
        draw_indicator_graph = self.checkBox_indicator_graph.isChecked() and indicator1 != None

        
        #############
        #  手动开关
        #############
        #draw_overlay_graph = False
        #draw_indicator_graph = False
        
 
        ###########
        # 绘图系统
        ###########
        self.mainGraph = MainGraph(stock_data)

        # Layout 
        self.layout = SimpleLayout(stock_data)
        self.layout.slope = slope
        self.layout.log_coord = log_coord
        self.layout.margin = margin
        self.layout.line_width = self.doubleSpinBox_linewidth.value()
        # Main
        self.layout.main_graph = self.mainGraph

        # Overlay 1
        self.layout.is_drawing_overlay1 = draw_overlay_graph1
        self.layout.overlay_graph1 =  overlay1
        # Overlay 2
        self.layout.is_drawing_overlay2 = draw_overlay_graph2
        self.layout.overlay_graph2 =  overlay2

        # Indicator 1
        self.layout.is_drawing_indicator = draw_indicator_graph
        self.layout.indicator_graph = indicator1
        self.layout.is_drawing_pc = self.checkBox_pc.isChecked()
        self.layout.is_draw_grid = self.checkBox_grid.isChecked()
        self.layout.draw_grid_3d = self.checkBox_grid_3d.isChecked()
        
        # 3D logo
        self.layout.logo = Draw3DLogo()
        
        self.main_view.SetLayout(self.layout)
        
        self.empty = False

        # Refresh
        self.layout.zoom = self.ComputeZoom( stock_data['data_length'],  self.main_view.rect() )
        self.main_view.repaint()

    def ComputeZoom(self,  LEN,  rect):
        self.layout.ComputeLayout(rect)
        return (self.layout.graph_width) / LEN

    @pyqtSlot(float)
    def on_doubleSpinBox_linewidth_valueChanged(self,  value):
        if not self.empty:
            self.layout.line_width = value
            self.main_view.repaint()
            print( "layout.line_width: %r"%value)

    @pyqtSlot(float)
    def on_doubleSpinBox_margin_valueChanged(self,  value):
        if not self.empty:
            self.layout.margin = value
            self.main_view.repaint()
            print( "layout.margin: %r"%value)
        
    @pyqtSlot(bool)
    def on_checkBox_gbbq_clicked(self, checked):
        if not self.empty:
            print( "layout.use_gbbq: %r"%checked)
            self.loadButtonClicked(None)
            
    @pyqtSlot(bool)
    def on_checkBox_logcoord_clicked(self, checked):
        if not self.empty:
            print( "layout.logcoord: %r"%checked)
            self.loadButtonClicked(None)
            
    @pyqtSlot(bool)
    def on_checkBox_overlay1_clicked(self, checked):
        if not self.empty:
            self.layout.is_drawing_overlay1 = checked
            self.main_view.repaint()
            print( "layout.is_drawing_overlay1: %r"%checked)

    @pyqtSlot(bool)
    def on_checkBox_overlay2_clicked(self, checked):
        if not self.empty:
            self.layout.is_drawing_overlay2 = checked
            self.main_view.repaint()
            print( "layout.is_drawing_overlay2: %r"%checked)

    @pyqtSlot(bool)
    def on_checkBox_indicator_graph_clicked(self, checked):
        if not self.empty:
            self.layout.is_drawing_indicator = checked
            self.main_view.repaint()
            print( "layout.is_drawing_indicator: %r"%checked)

        
    @pyqtSlot(bool)
    def on_checkBox_grid_3d_clicked(self, checked):
        if not self.empty:
            self.layout.draw_grid_3d = checked
            self.main_view.repaint()
            print( "layout.draw_grid_3d: %r"%checked)

    @pyqtSlot(bool)
    def on_checkBox_grid_clicked(self, checked):
        if not self.empty:
            self.layout.is_draw_grid = checked
            self.main_view.repaint()
            print( "layout.is_draw_grid: %r"%checked)

    @pyqtSlot(bool)
    def on_checkBox_pc_clicked(self, checked):
        if not self.empty:
            self.layout.is_drawing_pc = checked
            self.main_view.repaint()
            print( "layout.is_drawing_pc: %r"%checked)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    if False:
        fmt = QSurfaceFormat()
        fmt.setSamples(4)
        QSurfaceFormat.setDefaultFormat(fmt)
    
    MainWindow = EditorMain()
    MainWindow.show()
    sys.exit(app.exec_())
