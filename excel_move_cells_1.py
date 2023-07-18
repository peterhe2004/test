import openpyxl

# Load the Excel workbook
workbook = openpyxl.load_workbook('your_file.xlsx')

# Select the desired sheet
sheet = workbook['Sheet1']  # Replace 'Sheet1' with your sheet name

# Define the list of cell addresses you want to move
cell_addresses = ['B2', 'V2', 'D2']  # Add more cell addresses if needed

# Iterate over the cell addresses
for cell_address in cell_addresses:
    source_cell = sheet[cell_address]
    target_cell = sheet.cell(row=source_cell.row, column=source_cell.column - 1)
    target_cell.value = source_cell.value
    source_cell.value = None

# Save the modified workbook
workbook.save('your_file_modified.xlsx')
