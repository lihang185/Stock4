import sys
sys.path.append('C:/proj/Stock4')
import tdx
import matplotlib.pyplot as plt

tdxfile = tdx.TdxDayFile()
tdxfile.LoadFile("sh600036")
i=0;
b=10;


plt.plot(tdxfile.data['close'])

plt.show()
