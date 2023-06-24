import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('your_file.xlsx')

max_line_number = 

# Identify the rows that meet the conditions
condition1 = df['A'].notnull() & df.iloc[:, 1:].isnull().all(axis=1)
condition2 = df['A'].isnull() & df.iloc[:, 1:].notnull().any(axis=1)
rows_to_copy = df[condition1].index + 1  # Index of rows to copy (2nd line)
rows_to_copy = rows_to_copy[rows_to_copy <= max_line_number]  # Limit to max line number


# Copy the content from column 'A' of 1st line to column 'A' of 2nd line
df.loc[rows_to_copy, 'A'] = df.loc[rows_to_copy - 1, 'A'].values

# Display the updated DataFrame
print(df)


#<<Another way to achieve it>>
import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('your_file.xlsx')

# Define the maximum line number
max_line_number = 10  # Adjust this value as per your requirement

# Identify the rows that meet the conditions within the specified range
condition1 = (df['A'].notnull() & df.iloc[:, 1:].isnull().all(axis=1)).astype(int)
condition2 = (df['A'].isnull() & df.iloc[:, 1:].notnull().any(axis=1)).astype(int)
condition2_shifted = condition2.shift(-1)

# Copy the content from column 'A' of the 1st line to column 'A' of the 2nd line
df.loc[condition2_shifted.astype(bool) & (df.index <= max_line_number), 'A'] = df.loc[condition1.astype(bool), 'A'].values

# Display the updated DataFrame
print(df)






import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('your_file.xlsx')

# Define the maximum line number
max_line_number = 10  # Adjust this value as per your requirement

# Identify the rows that meet the conditions within the specified range
condition1 = (df['A'].notnull() & df.iloc[:, 1:].isnull().all(axis=1)).astype(int)
condition2 = (df['A'].isnull() & df.iloc[:, 1:].notnull().any(axis=1)).astype(int)

# Copy the content from column 'A' of the 1st line to column 'A' of the 2nd line
df.loc[(condition2.shift(-1).fillna(0).astype(bool)) & (df.index <= max_line_number), 'A'] = df.loc[condition1.astype(bool), 'A'].values

# Display the updated DataFrame
print(df)








import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('shCDP.xlsx')

# Define the maximum line number
max_line_number = 10  # Adjust this value as per your requirement

# Iterate over the rows of the DataFrame in reverse order
for i in range(len(df)-1, 0, -1):
    # Check the conditions for copying
    if pd.isna(df.at[i, 'A']) and not pd.isna(df.at[i-1, 'A']) and df.loc[i, 'B':'E'].notnull().any():
        df.at[i, 'A'] = df.at[i-1, 'A']  # Copy the content from cell A1 to A2
        df = df.drop(i-1)  # Delete the row i-1

# Reset the index after deleting rows
df = df.reset_index(drop=True)

# Save the updated DataFrame to a new Excel file
df.to_excel('shCDP_v1.xlsx', index=False)

# Display the updated DataFrame
print(df)
