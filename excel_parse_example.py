import pandas as pd
import sys


print(df.columns)

df = df.rename(columns={'Column1': 'A', 'Column2': 'B', 'Column3': 'C', ...})


#merged_column = df.loc[:, 'A':'L'].astype(str).apply(':'.join, axis=1)

df['Merged'] = merged_column

merged_column = df.loc[:, 'A':'L'].astype(str).apply(lambda row: ':'.join(row), axis=1)
df['Merged'] = merged_column


df['E'] = ''
copy_flag = False

for i, row in df.iterrows():
    if row['A'].startswith('ca0'):
        copy_flag = True
        copied_value = row['A']
    elif copy_flag:
        df.at[i, 'E'] = copied_value

df = df[df['A'].apply(lambda x: not x.startswith('ca0'))]




