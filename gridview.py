import sys
from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as QtWidgets
import StockView
StockView.g_Enable_OpenGL()

from StockView import StockView
from StockView.GridLayout import GridLayout
from StockView.Draw3DLogo import Draw3DLogo

from tdx import DataCenter

app = QtWidgets.QApplication(sys.argv)

layout = GridLayout(4, 4)
layout.SetDataCenter(DataCenter)

dm00 = DataCenter()
if dm00.LoadStockData("sh999999",  False, 1.0):
    layout.CreateView(0, 0, dm00.data)
dm10 = DataCenter()
if dm10.LoadStockData("sh600028",  False, 1.0):
    layout.CreateView(1, 0, dm10.data)
dm20 = DataCenter()
if dm20.LoadStockData("sz000002",  False, 1.0):
    layout.CreateView(2, 0, dm20.data)
dm30 = DataCenter()
if dm30.LoadStockData("sh600519",  False, 1.0):
    layout.CreateView(3, 0, dm30.data)


dm01 = DataCenter()
if dm01.LoadStockData("sh600036",  False, 1.0):
    layout.CreateView(0, 1, dm01.data)
dm11 = DataCenter()
if dm11.LoadStockData("sh601988",  False, 1.0):
    layout.CreateView(1, 1, dm11.data)
dm21 = DataCenter()
if dm21.LoadStockData("sh601398",  False, 1.0):
    layout.CreateView(2, 1, dm21.data)
dm31 = DataCenter()
if dm31.LoadStockData("sh601939",  False, 1.0):
    layout.CreateView(3, 1, dm31.data)


dm02 = DataCenter()
if dm02.LoadStockData("sz000402",  False, 1.0):
    layout.CreateView(0, 2, dm02.data)
dm12 = DataCenter()
if dm12.LoadStockData("sh600663",  False, 1.0):
    layout.CreateView(1, 2, dm12.data)
dm22 = DataCenter()
if dm22.LoadStockData("sh600383",  False, 1.0):
    layout.CreateView(2, 2, dm22.data)
dm32 = DataCenter()
if dm32.LoadStockData("sh600048",  False, 1.0):
    layout.CreateView(3, 2, dm32.data)


dm03 = DataCenter()
if dm03.LoadStockData("sz000858",  False, 1.0):
    layout.CreateView(0, 3, dm03.data)
dm13 = DataCenter()
if dm13.LoadStockData("sz000799",  False, 1.0):
    layout.CreateView(1, 3, dm13.data)
dm23 = DataCenter()
if dm23.LoadStockData("sz000596",  False, 1.0):
    layout.CreateView(2, 3, dm23.data)
dm33 = DataCenter()
if dm33.LoadStockData("sz000568",  False, 1.0):
    layout.CreateView(3, 3, dm33.data)


    
layout.SetMainView(1, 0)

layout.GetView(0, 3).logo = Draw3DLogo()
layout.GetView(0, 3).LOGO_WIDTH = 100
layout.GetView(0, 3).LOGO_HEIGHT = 100


form = QtWidgets.QMainWindow()
stock4 = StockView(form)
stock4.layout = layout
layout.widget = stock4

form.setCentralWidget(stock4)  
form.show()
app.exec_()   
    
