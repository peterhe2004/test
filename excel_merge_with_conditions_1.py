import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_csv('shCDP3.csv')

# Define the maximum line number
max_line_number = 10  # Adjust this value as per your requirement

# Iterate over the rows of the DataFrame in reverse order
for i in range(len(df)-1, 0, -1):
    # Check the conditions for copying
    if pd.isna(df.iloc[i, 1]) and not pd.isna(df.iloc[i-1, 1]) and not pd.isna(df.iloc[i, 2]):
        df.iloc[i, 1] = df.iloc[i-1, 1]  # Copy the content from cell A1 to A2
        df = df.drop(i-1)  # Delete the row i-1

# Reset the index after deleting rows
df = df.reset_index(drop=True)

# Save the updated DataFrame to a new Excel file
df.to_csv('shCDP4.csv', index=False)

# Display the updated DataFrame
print(df)