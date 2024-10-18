import pandas as pd

# Path to the input Excel file
input_file = 'input.xlsx'

# Path to the output Excel file
output_file = 'output.xlsx'

# Read the input Excel file into a DataFrame
df = pd.read_excel(input_file)

# Loop through each row and create a separate sheet for each row in a transposed format
for index, row in df.iterrows():
    # Create a new DataFrame with a single row from the original DataFrame
    transposed_df = pd.DataFrame(row).T

    # Get the value from the first cell to use as the sheet name
    sheet_name = str(row[0])

    # Save the transposed DataFrame to a new sheet in the output Excel file
    with pd.ExcelWriter(output_file, mode='a') as writer:
        transposed_df.to_excel(writer, sheet_name=sheet_name, index=False)
