import openpyxl
import pandas as pd

# Load the Excel workbook
workbook = openpyxl.load_workbook('pdtest1.xlsx')

# Select the desired sheet
sheet = workbook['pdtest1']  # Replace 'Sheet1' with your sheet name

# Define the list of cell addresses you want to move
cell_addresses = ['B3', 'C3', 'D3']  # Add more cell addresses if needed

# Iterate over the cell addresses
for cell_address in cell_addresses:
    source_cell = sheet[cell_address]
    target_cell = sheet.cell(row=source_cell.row, column=source_cell.column - 1)
    target_cell.value = source_cell.value
    source_cell.value = None

# Save the modified workbook
workbook.save('pdtest2.xlsx')
