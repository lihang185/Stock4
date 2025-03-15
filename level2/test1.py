import l2file
import time

def Dump(a):
  deal_count = a.DealCount()

  for i in range(30):
    (id_, time_, is_sell, volume, price, buy_id, buy_flags, sell_id, sell_flags) = a.DealInfo(i)

    buy_order = a.BuyOrderInfoById(buy_id)

    sell_order = a.SellOrderInfoById(sell_id)
    
    buy_desc = ''
    if not (buy_flags & 1):
        buy_desc += '<'
    else:
        buy_desc += ' '
    
    buy_desc += "%5d"%buy_order[2]
    
    if not (buy_flags & 2):
        if buy_order[4]: # finished
            buy_desc += '>'
        else:
            buy_desc += 'x'
    else:
        buy_desc += ' '

    sell_desc = ""
    if not (sell_flags & 1):
        sell_desc += '<'
    else:
        sell_desc += ' '
        
    sell_desc +=  "%5d"%sell_order[2]
    
    if not (sell_flags & 2):
        if sell_order[4]: # finished
            sell_desc += '>'
        else:
            sell_desc += 'x'
    else:
        sell_desc += ' '
        
    if is_sell:
        B_desc = 'S'
    else:
        B_desc = 'B'
        
    st_time = time.localtime(time_)
    time_desc = "%2d:%2d"%(st_time.tm_hour, st_time.tm_min)
        
    print( "%4d %s %2.2f  "%(id_+1, time_desc, price), B_desc, sell_desc, "  ->  ", buy_desc,  buy_order[3])


def ComputeOrder(l2file):
    
    count =l2file.SellOrderCount()
    
    list_ = [0.0] * 250
    
    for i in range(count):
        id_,  price,  volume,  act_vol,  finished, deal_count = l2file.SellOrderInfo(i)
        
        index = int(volume / 1000)
        
        list_[index] += act_vol
        
    return list_


l2file = drawcandle.L2DayFile()

ret = l2file.LoadFile("C:/proj/Stock4/test/000058")

if ret:
  print('ok')
else:
  print('error')
  
list = ComputeOrder(l2file)

#Dump(l2file)

import matplotlib.pyplot as plt

x = range(0, 250)

plt.bar(x, list)

plt.show()

del l2file
