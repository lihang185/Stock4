import struct
from enum import Enum
import pandas
from os import path

class Bourse(Enum):
    sh = 0
    sz = 1
    
class StockCode:
    sh = 0
    sz = 1
    
    def __init__(self):
        self.bourse = StockCode.sh
        self.code = '600000'
        
    def ParseString(self,  code_string):
        if len(code_string) != 8:
            return False
        
        str_bourse = code_string[0:2]
        str_bourse = str_bourse.upper()
        if str_bourse =='SH':
            self.bourse = StockCode.sh
        elif str_bourse =='SZ':
            self.bourse = StockCode.sz
        else:
            return False
            
        str_code = code_string[2:8]
        self.code = str_code
        
        return True
        
    #def FormatCode(self):
    #    return '%06d' % self.code
        
    def ToString(self):
        code = ''
        if self.bourse == StockCode.sh:
            code = 'SH' + self.code
        else:
            code = 'SZ' + self.code
        return code
        


class GbbqData:
    def __init__(self):
        filename = path.dirname(__file__) + "/dividend1221.csv"
        self.LoadFromCSV(filename)
        self.empty = True
        
    def LoadFromCSV(self,  filename):
        self.data = pandas.read_csv(filename,  dtype =  {'date': int})
        #self.data = pandas.read_csv(filename)
        
    def Compute(self,  stockid,  original_data):
        if not original_data:
            return
            
        self.T = original_data['date']
        CLOSE = original_data['close']
        
        query = self.data[self.data['code'] == stockid ]
        if query.empty:
            self.empty = True
            return
            
        table = {"date":[self.T[0]], "totalAdd":[0],  "totalMulti":[1], "totalDec":[0],  "refv":[CLOSE[0]]}
        
        totalAdd = 0.0
        totalMulti = 1.0
        totalDec = 0.0
        for i,  row in query.iterrows():
            add = row.Dividends
            multi = (1.0 + row.BonusShares) * (1.0 + row.Allotment)
            dec = row.AllotmentPrice * row.Allotment
            
            # find date
            t, x = self.FindFast(row.date)
            assert(t==0)
            
            refv = CLOSE[x]
            idate = self.T[x]
            
            totalDec = ( totalDec + dec ) / multi;
            totalAdd = ( totalAdd + add ) / multi;
            totalMulti *= multi;
            
            if idate in table['date']:
                index = table['date'].index(idate)
                table['date'][index]=self.T[x]
                table['totalAdd'][index]=totalAdd
                table['totalMulti'][index]=totalMulti
                table['totalDec'][index]=totalDec
                table['refv'][index]=refv
            else:
                table['date'].append(self.T[x])
                table['totalAdd'].append(totalAdd)
                table['totalMulti'].append(totalMulti)
                table['totalDec'].append(totalDec)
                table['refv'].append(refv)
            #d = { "date":row.date,  "totalAdd":totalAdd,  "totalMulti":totalMulti, "totalDec":totalDec}
            #rehab = rehab.append(d,  ignore_index=True)
            #rehab = rehab.append(d)
            
        left   = pandas.DataFrame({'date':self.T})
        right = pandas.DataFrame(table)
        
        self.rehab_data = pandas.merge(left, right, on='date', how='left').fillna(method='ffill')
        
        self.empty = False
        
        #print(self.rehab_data)
        
    def FindFast(self, idate):
        T = self.T
        if idate < T[0]:
            return(1, 0)
        for x, d in enumerate(T):
            if d >= idate:
                return (0, x)
        return (2, len(T)-1)

    def Rehabilitation(self,  values):
        if self.empty:
            return values
        new = (values + self.rehab_data.totalAdd - self.rehab_data.totalDec) * self.rehab_data.totalMulti
        return new


class TdxDayFile:
    config_data_path = "C:/zd_zsone"

    def __init__(self):
        self.gbbq = None

    def LoadFile( self, stock_code):

        filename=''
        if stock_code.bourse == StockCode.sh:
            filename = TdxDayFile.config_data_path + '/vipdoc/sh/lday/sh' + stock_code.code + ".day"
        else:
            filename = TdxDayFile.config_data_path + '/vipdoc/sz/lday/sz' + stock_code.code + ".day"
          
        f = open(filename, 'rb')

        original_data = { "date":[],  "type":[],  "open":[],  "high":[],  "low":[],  "close":[],  "amount":[],  "vol":[]}

        while(True):
            bytes = f.read(32)
            if bytes == None or len(bytes) != 32:
                break
            
                
            int_date, int_open, int_high, int_low, int_close, float_amount, int_vol, reserved = struct.unpack('iiiiifii', bytes)
            
            # 奇怪的数据 BUG
            if int_high == int_low:
                int_high = int_low+1

            # 在这里就检查出涨跌类型
            # 以免转成浮点数难以判断
            if int_close == int_open:
                type = 2
            else:
                type = 0 if int_close > int_open else 1
            
            original_data['date'].append(int_date)
            original_data['type'].append(type)
            original_data['open'].append(float(int_open) / 100)
            original_data['high'].append(float(int_high) / 100)
            original_data['low'].append(float(int_low) / 100)
            original_data['close'].append(float(int_close) / 100)
            original_data['amount'].append(float_amount)
            original_data['vol'].append(float(int_vol)/100)

        f.close()
        original_data['data_length'] = len(original_data['date'])

        self.original_data = original_data

        return True

    def LoadGbbq(self,  stock_code):
        self.gbbq = GbbqData()
        self.gbbq.Compute(stock_code.ToString(),  self.original_data)
            
if __name__ == '__main__':
    T = [20080101, 20080601, 20200211]
    tb = TimeAxis(T)
    tb.Build()
    
    d1 = tb.FindDate(20070101)
    d2 = tb.FindDate(20080601)
    d3 = tb.FindDate(20200214)
    #index = test(T, 20080601)
    
    
    t = TimeAxis.ConvertIDate(20081103)


if __name__ == "__main__":
      tdx = TdxDayFile()
      tdx.LoadFile("sh000001.day")
  
