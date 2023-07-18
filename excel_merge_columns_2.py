import pandas as pd

# Read the Excel file
df = pd.read_excel('pdtest1.xlsx', sheet_name=0, header=None)

# Define the columns you want to merge
# column1 = 'C'  # Replace 'A' with the desired column name or index
# column2 = 'B'  # Replace 'B' with the desired column name or index

# Merge the columns
# df[column1] = df[column1].astype(str) + df[column2].astype(str)
# df[column2] = None

column1_index = 3
column2_index = 4

# Assuming you have column indices in variables 'column1_index' and 'column2_index'
df.iloc[:, column1_index] = df.iloc[:, column1_index].astype(str) + df.iloc[:, column2_index].astype(str)
df.iloc[:, column2_index] = None


# Save the modified DataFrame to Excel
df.to_excel('pdtest2.xlsx', index=False, header=False)
