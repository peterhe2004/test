import pandas as pd

file1 = "inventory_1.xlsx"
file1 = "inventory_2.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

df1 = df1.set_index("ID")
df2 = df2.set_index("ID")

diff = df1.compare(df2)

diff.to_excel("Solarwinds_differences.xlsx")


# Alternative approach to compare the two DataFrames
if df1.shape != df2.shape:
    print("The files have different shapes and cannot be compared.")
else:
    differences = df1 != df2
    if differences.any().any():
        print("The files have differences:")
        print(df1[differences])
        print(df2[differences])
    else:
        print("The files are identical.")




