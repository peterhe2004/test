import pandas as pd

# Assuming df is your DataFrame
df = pd.read_csv('shCDP1.csv')

# Ensure the DataFrame has column 15
while df.shape[1] < 16:
    df[df.shape[1]] = ""

# Add extra columns to match the structure of output csv
for i in range(6, 16):
    df[str(i)] = ''

# Group data by 'index' and 'device'
groups = df.groupby(['index', 'device'])

for name, group in groups:
    # Filter rows where 'neighbor' starts with 'SEP'
    sep_rows = group[group['neighbor'].str.startswith('SEP')]
    
    if not sep_rows.empty:
        # Join 'local_port' of all 'SEP' rows
        merged_ports = ';'.join(sep_rows['local_port'])
        
        # Update the 10th column of the first row in the current group
        df.loc[group.index[0], '10'] = merged_ports

# Save the dataframe as a csv file
df.to_csv('shCDP2.csv', index=False)
