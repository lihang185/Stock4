


from .StockView import (StockViewNormal,StockViewOpenGL)

from .MainGraph import MainGraph,  MainGraphGL
from .GraphEngine import GraphEngine, GraphEngineGL
from .LineSegmentGraph import LineSegmentData, LineSegmentGraph, LineSegmentGraphGL
from .BaseIndicators import MACD, VOLIndicator, MAIndicator
from .Layout import SimpleLayout,  EmptyLayout

StockView = StockViewNormal

def g_Enable_OpenGL():
    global StockView,  MainGraph,  GraphEngine,  LineSegmentGraph
    StockView = StockViewOpenGL
    MainGraph = MainGraphGL
    GraphEngine = GraphEngineGL
    LineSegmentGraph = LineSegmentGraphGL
