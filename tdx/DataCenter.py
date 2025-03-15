import numpy
import time
import math

from .tdxfile import *


class TimeAxis:
    def __init__(self,  T):
        self.T = T
        self.LEN = len(T)
        self.year_list = []
        
    def Build(self):
        # furuture
        self.future_list = self.BuildTimeList(self.T[-1], 2040, False)
        # before
        self.befor_list = self.BuildTimeList(self.T[0], 1990, True)
        
        ############
        LEN = len(self.befor_list)
        befor = [(-LEN+i, idate) for i,  idate in enumerate(self.befor_list)]
        ############
        current = [(i, idate) for i,  idate in enumerate(self.T)]
        ############
        LEN = len(self.T)
        future = [(LEN+i, idate) for i,  idate in enumerate(self.future_list)]
        ############
        
        # total T
        self.TT = befor + current + future

        self.BuildYearList()
        
    def BuildYearList(self):
        list = []
        
        last_year = 0
        for x, idate in self.TT:
            (year, month, day) = TimeAxis.FromIDate(idate)
            if year > last_year:
                item = (x, idate)
                list.append(item)
                last_year = year
        last_year = 0 
  
        self.year_list = list
        
    def FindYear(self, year):
        idx=0
        for x, idate in self.year_list:
            y, m, d = TimeAxis.FromIDate(idate)
            if y == year:
                return idx
            idx+=1
        return idx
        
    def FromIDate(idate):
        year = idate // 10000
        dm = idate % 10000
        month = dm//100
        day = dm%100
        return (int(year), int(month), int(day))
    
    def ToIdate(year, month, day):
        idate = year * 10000 + month * 100 + day;
        return int(idate)
        
        
    def BuildTimeList(self,  start, to_year,  reverse):
        list = []

        # Get Last Date
        (year, month, day) = TimeAxis.FromIDate(start)
        ts = time.mktime((year, month, day, 12, 0, 0, 0, 0, 0))
        
        while True:
            step = 24 * 3600
            if reverse:
                ts -= step
            else:
                ts += step
            
            fmt = time.localtime(ts)
            if reverse and fmt.tm_year < to_year or not reverse and fmt.tm_year > to_year:
                break
            if  fmt.tm_wday == 5 or fmt.tm_wday == 6:
                continue

            idate = TimeAxis.ToIdate(fmt.tm_year, fmt.tm_mon, fmt.tm_mday)
            #item = ( self.LEN + len(self.future_list2),  idate)
            list.append(idate)
            
        if reverse:
            list.reverse()
        
        return list
        
    def FindDate(self, idate):
        for x, d in self.TT:
            if d > idate:
                return x
        return self.TT[-1][0]
        
    def FindFast(self, idate):
        if idate < self.T[0]:
            return(1, 0)
        for x, d in self.T:
            if d > idate:
                return (0, x)
        return (2, 0)
                
class DataCenter:
    def __init__(self):
        self.data = None
        self.gbbq = None
        
    def LoadStockData( self, stockid, use_gbbq,  slope):
        self.use_gbbq = use_gbbq
        
        stock_code = StockCode()
        if not stock_code.ParseString(stockid):
            return False
            
        self.stock_code = stock_code
        
        self.tdxfile = TdxDayFile()
        if not self.tdxfile.LoadFile(stock_code):
            return

        original_data = self.tdxfile.original_data
        self.original_data = self.tdxfile.original_data

        self.LEN = original_data['data_length']
        self.timeAxis = TimeAxis(original_data['date'] )
        self.timeAxis.Build()
        
        self.ComputeSlopeData(slope)
        
        if use_gbbq:
            self.tdxfile.LoadGbbq(stock_code)
            self.gbbq = self.tdxfile.gbbq
        
        self.data = {}
        self.data['code'] = stock_code.ToString()
        self.data['LEN']  = original_data['data_length']
        self.data['data_length']  = original_data['data_length']
        self.data['date']  = original_data['date']
        self.data['type'] = original_data['type']
        self.data['open'] = list(self.Conversion(original_data['open']))
        self.data['high'] = list(self.Conversion(original_data['high']))
        self.data['low'] = list(self.Conversion(original_data['low']))
        self.data['close'] = list(self.Conversion(original_data['close']))
        self.data['vol'] = original_data['vol'] 
        self.data['TimeAxis'] = self.timeAxis


        return True
        
    def ComputeSlopeData(self,  slope):
        
        T = self.original_data['date']
        year_list = self.timeAxis.year_list
        
        current_year = 0
        
        list_ = []
        num_years = 0
        year_days = 0
        for x in range(self.LEN-1, -1, -1):
            idate = T[x]
            year, month, day = TimeAxis.FromIDate(idate)
            
            if year != current_year:
                year_index= self.timeAxis.FindYear(year)
                current_year = year
                year_days = year_list[year_index+1][0] - year_list[year_index][0]
                start_x = year_list[year_index+1][0]
                start_slope =  math.pow(slope, num_years)
                num_years+=1
            
            scale = (start_x - x)/year_days
            cur_slope =  math.pow(slope, scale) * start_slope
            list_.append(cur_slope)
        list_.reverse()
        self.slope_data = list_
        
    def LoadFromCSV(self, filename, column):
        filename = path.dirname(__file__) + '/'+filename+'.csv'
        data = pandas.read_csv(filename,  dtype =  {'date': int})
        
        stock_str = self.stock_code.ToString()
        query = data[data['code'] == stock_str ]
        if query.empty:
            return None
        
        list = []
        for i,  row in query.iterrows():
            value = row[column]
            if value < 0.01:
                continue
            
            value = self.RehabilitationByRef(row.date, value)
            
            item = (row.date, value)
            list.append(item)
        
        return list
        
    def FindFast(self, idate):
        T = self.data['date']
        if idate < T[0]:
            return(1, 0)
        for x, d in enumerate(T):
            if d > idate:
                return (0, x)
        return (2, len(T)-1)
        
    def RehabilitationByRef(self, idate, y):
        #find date
        (t, x) = self.FindFast(idate)
        
        if self.use_gbbq and t==0:
            rehab_data = self.gbbq.rehab_data
            scale = y / rehab_data.refv[x]
            y = (y + rehab_data.totalAdd[x]*scale - rehab_data.totalDec[x]*scale) * rehab_data.totalMulti[x]
        
        y *= self.slope_data[x]
        return y
 
    def Conversion(self,  S):
        A = numpy.array(self.gbbq.Rehabilitation(S)) if self.use_gbbq else numpy.array(S)
        B = A * self.slope_data
        return B
