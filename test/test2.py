import pandas as pd

left = pd.DataFrame({'date': ['20080101', '20080102', '20080103', '20080104', '20080105', '20080106', '20080107', '20080108', '20080109', '20080201', '20080205']})

right = pd.DataFrame({'date': ['20080101', '20080105', '20080201', '20080205'],
                     'add': [0.1, 0.35, 0.88, 1.15],
                     'multi': [1.0, 1.2, 1.4, 1.9],
                     'dec': [0.2, 0.4, 0.6, 2.0]})


data = pd.merge(left, right, on='date', how='left')

data.fillna(method='ffill')

