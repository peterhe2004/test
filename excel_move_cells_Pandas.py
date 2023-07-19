import pandas as pd

# Read the Excel file into a DataFrame
df = pd.read_excel('pdtest1.xlsx', sheet_name='Sheet1')

# Define the column indices you want to move
column_indices = [4, 3, 2]  # Replace with the desired column indices

# Iterate over the column indices and move the cells
for i in range (len(df)):
    condition = df.iloc[i, 2] is None
    if condition:
            print(condition)
            for col_idx in column_indices:
                df.iloc[:, col_idx + 2] = df.iloc[:, col_idx].astype(str)
                df.iloc[:, col_idx] = None

# Save the modified DataFrame to Excel
df.to_excel('pdtest2.xlsx', index=False)
