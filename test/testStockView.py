import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
sys.path.append('C:/proj/Stock4')
from StockView import *
import tdx

tdxfile = tdx.TdxDayFile()
#tdxfile.LoadFile("sh999999")
tdxfile.LoadFile("sh600036")
#tdxfile.LoadFile("sh601500")


app = QApplication(sys.argv)

stock4 = StockView()
stock4.SetCandleChartData(tdxfile.original_data)
stock4.BuildData()

form = QMainWindow()
form.setCentralWidget(stock4)  
form.show()
app.exec_()   
    
