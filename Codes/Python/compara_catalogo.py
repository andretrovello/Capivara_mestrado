import pandas as pd

data_PHANGS = pd.read_csv('PHANGS_catalog.csv')
data_TIMER = pd.read_csv('TIMER_catalog.csv')

df_PHANGS = pd.DataFrame(data_PHANGS)
df_TIMER = pd.DataFrame(data_TIMER)

galaxias_TIMER_PHANGS = set(df_PHANGS['Galaxy']) & set(df_TIMER['Galaxy'])
print(galaxias_TIMER_PHANGS)