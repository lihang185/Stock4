
from os import path
import numpy
import pandas

def finance_load_db(stockid):
    filename = path.dirname(__file__) + "/finance_db.csv"
    data = pandas.read_csv(filename,  dtype =  {'date': int})
    
    query = data[data['code'] == stockid ]
    if query.empty:
        return None
    
    list = []
    for i,  row in query.iterrows():
        item = (row.date, row.book_value)
        list.append(item)
        
    return list
