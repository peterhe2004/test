import re
import pandas as pd

df = pd.read_excel("inventory_2.xlsx")
df.columns = df.columns.str.strip()

COL = "show_ver"
if COL not in df.columns:
    raise SystemExit(f"Column '{COL}' not found. Available: {list(df.columns)}")

patterns = {
    "TACACS_Key": re.compile(r'(?im)^\s*(key\s+7\s+[^\r\n]+)'),
    "SCP_Server": re.compile(r'(?im)^\s*(ip\s+scp\s+server.*)$'),
    "Lobby_Admin": re.compile(r'(?i)\blobby-admin\b'),
    "Serial_Number": re.compile(r'(?im)system\s+serial\s+number\s*:\s*([A-Za-z0-9]{11})')
}

def extract_and_count(text, regex):
    if pd.isna(text):
        return pd.Series([None, 0])

    matches = regex.findall(str(text))
    if not matches:
        return pd.Series([None, 0])

    cleaned = []
    for m in matches:
        if isinstance(m, tuple):
            cleaned.append(m[0])
        else:
            cleaned.append(m)

    return pd.Series(["; ".join(cleaned), len(cleaned)])

for name, regex in patterns.items():
    df[[f"{name}_Extracted", f"{name}_Count"]] = df[COL].apply(
        lambda x: extract_and_count(x, regex)
    )

print("\n=== Total Counts ===")
for name in patterns:
    print(f"{name}: {df[f'{name}_Count'].sum()}")

df.to_excel("CVE_output.xlsx", index=False)
print("Wrote: CVE_output.xlsx")