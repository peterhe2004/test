import openpyxl

# Load the Excel workbook
workbook = openpyxl.load_workbook('your_file.xlsx')

# Select the desired sheet
sheet = workbook['Sheet1']  # Replace 'Sheet1' with your sheet name

# Define the list of cell addresses you want to move
cell_addresses = ['B2', 'V2', 'D2']  # Add more cell addresses if needed

# Define the function to move the cell contents
move_cells = lambda src, tgt: (tgt.value := src.value) or (src.value := None)

# Iterate over the cell addresses and move the cell contents
for cell_address in cell_addresses:
    move_cells(sheet[cell_address], sheet.cell(row=src.row, column=src.column - 1))

# Save the modified workbook
workbook.save('your_file_modified.xlsx')
