
import sys

sys.path.append('C:/proj/Stock4')
from StockView.drawcandle import L2DayFile


l2file = L2DayFile()

try:
    l2file.LoadFile("C:/proj/Stock4/test/000058")
    ff = 0
except FileExistsError:
    ff = 123

  
count = l2file.DealCount()

try:
    a = l2file.DealInfo(count)
except IndexError:
    a = 10

k = 0

