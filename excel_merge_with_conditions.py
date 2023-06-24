import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('your_file.xlsx')

# Identify the rows that meet the conditions
condition1 = df['A'].notnull() & df.iloc[:, 1:].isnull().all(axis=1)
condition2 = df['A'].isnull() & df.iloc[:, 1:].notnull().any(axis=1)
rows_to_copy = df[condition1].index + 1  # Index of rows to copy (2nd line)

# Copy the content from column 'A' of 1st line to column 'A' of 2nd line
df.loc[rows_to_copy, 'A'] = df.loc[rows_to_copy - 1, 'A'].values

# Display the updated DataFrame
print(df)



