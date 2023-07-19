import pandas as pd

# Read the Excel file into a DataFrame
df = pd.read_excel('pdtest1.xlsx', sheet_name='Sheet1', header=None)

# Ensure the DataFrame has column 15
while df.shape[1] < 16:
    df[df.shape[1]] = ""

# Iterate over the rows
for i in range(df.shape[0] - 1):
    if df.iloc[i+1, 3] == df.iloc[i, 3] and str(df.iloc[i+1, 4])[:3] == 'SEP':
        df.iloc[i, 15] += str(df.iloc[i+1, 5]) + ','

# If the last character of df.iloc[i, 15] is ',', remove it
for i in range(df.shape[0]):
    if df.iloc[i, 15].endswith(','):
        df.iloc[i, 15] = df.iloc[i, 15][:-1]

# Save the modified DataFrame to Excel
df.to_excel('pdtest2.xlsx', index=False)
