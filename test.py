import numpy as np
import pandas as pd

URL = 'sports.csv'

sports = pd.read_csv(URL)

active_sports = sports[sports['active'] == True]
print(active_sports)

# print(sports.describe)
# print('Column Names:', sports.iloc[0])
