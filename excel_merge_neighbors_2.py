import pandas as pd

# Assuming df is your DataFrame
df = pd.read_csv('shCDP1.csv')

# Ensure the DataFrame has column 15
while df.shape[1] < 16:
    df[df.shape[1]] = ""

# Function to find length of consecutive sequence in a specific column
def consecutive_length(df, start_index, column):
    val = df.iloc[start_index, column]
    length = 0
    for i in range(start_index, len(df)):
        if df.iloc[i, column] == val:
            length += 1
        else:
            break
    return length

for i in range(len(df)):
    # Calculate n based on consecutive strings in column 0
    n = consecutive_length(df, i, 0)
    if n > 1:  # If there are at least 2 same strings in a row
        for j in range(len(df)):
            # Calculate m based on consecutive strings in column 1
            m = consecutive_length(df, j, 1)
            if m > 1:  # If there are at least 2 same strings in a row
                # Check Condition 3
                if str(df.iloc[j, 4])[:3] == 'SEP':
                    # Merge string values
                    df.iloc[i, 10] = ','.join([str(df.iloc[l, 5]) for l in range(j, j + m)])



# Save the modified DataFrame to Excel
df.to_csv('shCDP2.csv', index=False)                    
