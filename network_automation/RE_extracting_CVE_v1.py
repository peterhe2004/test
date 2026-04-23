import re
import pandas as pd

# --- Load your file ---
df = pd.read_excel("inventory_2.xlsx")  # change to your file

# --- Make sure column names are clean and show them ---
df.columns = df.columns.str.strip()
print("Columns:", list(df.columns))

COL = "show_ver"   # <<-- CHANGE to your actual column name
if COL not in df.columns:
    raise SystemExit(f"Column '{COL}' not found. Available: {list(df.columns)}")

# block_rx = re.compile(
#     r'(?ims)'                                  # i = ignorecase, m = multiline (^ $), s = dot matches newline
#     r'^tacacs\s+server\s+[^\r\n]+'             # header line
#     r'(?:\r?\n)\s*address\s+ipv4\s+10'         # next line must be address ipv4 10...
#     r'(?:\.\d{1,3}){3}'                        # 10.x.x.x
#     r'.*?'                                     # rest of the block (non-greedy)
#     r'(?=^tacacs\s+server\b|\Z)'               # stop before next block or end of text
# )

block_rx = re.compile(
    r'(?ims)^tacacs\s+server\s+[^\r\n]+(?:\r?\n)\s*address\s+ipv4\s+10(?:\.\d{1,3}){3}.*?(?=^tacacs\s+server\b|\Z)'
)

print(f"Block regex: {block_rx.pattern}")

# Each key line inside the block
key_line_rx = re.compile(r'(?im)^\s*(key\s+7\s+[^\r\n]+)')
print({key_line_rx})

def extract_keys_from_paragraph(text):
    if text is None:
        return None
    s = str(text)
    keys = []
    for block in block_rx.findall(s):
        keys.extend(key_line_rx.findall(block))   # collect "key 7 ..." full lines
        # print(f"Found block:\n{block}\n")
    return "; ".join(keys) if keys else None


# --- Quickly check if the key phrase exists (case-insensitive) ---
mask_phrase = df[COL].str.contains(r"tacacs\s+server", case=False, na=False)
print(f"Rows containing 'tacacs server': {mask_phrase.sum()}")

# Show a few raw examples (repr helps visualize spaces/newlines)
print("\nSample rows that contain the phrase (repr shown):")
for s in df.loc[mask_phrase, COL].head(5):
    print(repr(s))


df["TACACS_Keys"] = df[COL].apply(extract_keys_from_paragraph)


# --- Save output to check ---
df.to_excel("CVE_output.xlsx", index=False)
print("\nWrote: result exported")
