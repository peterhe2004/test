import pandas as pd
from openpyxl import load_workbook

# Load sheet-A and sheet-B
sheet_a = pd.read_excel('path_to_sheet_A.xlsx')
sheet_b = pd.read_excel('path_to_sheet_B.xlsx')

# Extract the first 7 characters from sheet-A's 'A' column
sheet_a['Prefix'] = sheet_a['A'].str[:7]

# Merge data from sheet-B into sheet-A based on matching prefixes
merged_sheet = pd.merge(sheet_a, sheet_b, left_on='Prefix', right_on='A', how='inner')

# Save the merged sheet back to sheet-A
with pd.ExcelWriter('path_to_sheet_A.xlsx', engine='openpyxl') as writer:
    writer.book = load_workbook('path_to_sheet_A.xlsx')
    merged_sheet.to_excel(writer, sheet_name='SheetA', index=False)
    writer.save()
