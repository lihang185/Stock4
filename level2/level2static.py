import sys
import time

#import l2file
from l2file import L2DayFile

def SellOrderIter(obj):
    LEN = obj.SellOrderCount()
    for i in range(LEN):
        yield obj.SellOrderInfo(i)

def BuyOrderIter(obj):
    LEN = obj.BuyOrderCount()
    for i in range(LEN):
        yield obj.BuyOrderInfo(i)

class L2Static:
    def __init__(self, l2file):
        self.l2file = l2file

    def static(self, iter):
        #LEN =l2file.SellOrderCount()
        small = 0.0
        small_count = 0
        small_vol = 0
        normal = 0.0
        normal_count = 0
        normal_vol = 0
        big = 0.0
        big_count = 0
        big_vol = 0
        
        for pack in iter:
            order_id,  price,  volume,  act_vol,  finished, deal_count = pack
            
            #act_vol = act_vol // 100
            amount = volume * price
            act_amount = (act_vol * price)/10000
            
            act_vol /= 100
            
            if amount < 300000:
                small += act_amount
                small_count += 1
                small_vol += act_vol
            elif amount < 1000000:
                normal += act_amount
                normal_count +=1
                normal_vol += act_vol
            elif amount < 5000000:
                big += act_amount
                big_count+=1
                big_vol += act_vol

        print("finished")
        
        return {
            'small':small, 
            'small_count':small_count, 
            'small_vol':small_vol, 
            'normal':normal, 
            'normal_count':normal_count, 
            'normal_vol':normal_vol, 
            'big':big, 
            'big_count':big_count, 
            'big_vol':big_vol, 
        }
        
    def staticBuy(self):
        iter = BuyOrderIter(self.l2file)
        self.buy = self.static(iter)
        
    def staticSell(self):
        iter = SellOrderIter(self.l2file)
        self.sell = self.static(iter)



def print1():
    print("%10.2f %10.2f %5d"%( l2static.buy['small_vol'], l2static.buy['small'], l2static.buy['small_count'] ) )
    print( "%10.2f %10.2f %5d"%( l2static.buy['normal_vol'], l2static.buy['normal'], l2static.buy['normal_count'] ) )
    print( "%10.2f %10.2f %5d"%( l2static.buy['big_vol'], l2static.buy['big'], l2static.buy['big_count'] ) )
    print("------------------------")
    print( "%10.2f %10.2f %5d"%( l2static.sell['small_vol'], l2static.sell['small'], l2static.sell['small_count'] ) )
    print( "%10.2f %10.2f %5d"%( l2static.sell['normal_vol'], l2static.sell['normal'], l2static.sell['normal_count'] ) )
    print( "%10.2f %10.2f %5d"%( l2static.sell['big_vol'], l2static.sell['big'], l2static.sell['big_count'] ) )

def print2():
    print("%10d %10d %5d"%( round(l2static.buy['small_vol']), round(l2static.buy['small']), l2static.buy['small_count'] ) )
    print( "%10d %10d %5d"%( round(l2static.buy['normal_vol']), round(l2static.buy['normal']), l2static.buy['normal_count'] ) )
    print( "%10d %10d %5d"%( round(l2static.buy['big_vol']), round(l2static.buy['big']), l2static.buy['big_count'] ) )
    print("------------------------")
    print( "%10d %10d %5d"%( round(l2static.sell['small_vol']), round(l2static.sell['small']), l2static.sell['small_count'] ) )
    print( "%10d %10d %5d"%( round(l2static.sell['normal_vol']), round(l2static.sell['normal']), l2static.sell['normal_count'] ) )
    print( "%10d %10d %5d"%( round(l2static.sell['big_vol']), round(l2static.sell['big']), l2static.sell['big_count'] ) )


l2file = L2DayFile()

ret = l2file.LoadFile("C:/proj/Stock4/test/000058")
#ret = l2file.LoadFile("L:\\level2\\20190710\\600083")

l2static = L2Static(l2file)


start = time.perf_counter()
l2static.staticBuy()
func1_time = (time.perf_counter() - start ) * 1000


start = time.perf_counter()
l2static.staticSell()
func2_time = (time.perf_counter() - start ) * 1000

print1()

print("")
print("")
print("")

print2()

ok = 10

