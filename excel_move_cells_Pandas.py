import pandas as pd
import numpy as np

# Read the Excel file into a DataFrame
df = pd.read_excel('pdtest1.xlsx', sheet_name='Sheet1', header=None)
print(df.head())

# Define the column indices you want to move
column_indices = [4, 3, 2]  # Replace with the desired column indices

# Add additional empty columns if necessary
max_idx = max(column_indices)
if max_idx + 2 >= df.shape[1]:
     for i in range(df.shape[1], max_idx + 3):
          df[i] = np.nan


# Iterate over the column indices and move the cells
for i in range(df.shape[0]):
    condition = pd.isna(df.iloc[i, 2])
    if condition:
            print(f'Row {i+1} column 3 is NaN: {condition}')
            for col_idx in column_indices:
                df.iloc[i, col_idx + 2] = df.iloc[i, col_idx]
                df.iloc[i, col_idx] = np.nan
 
# Save the modified DataFrame to Excel
df.to_excel('pdtest2.xlsx', index=False)
