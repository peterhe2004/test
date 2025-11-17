import pandas as pd
import math

# Load Excel
path = "IPschemaTest_v1.xlsx"   # change path as needed
device = pd.read_excel(path, sheet_name="device")
schema = pd.read_excel(path, sheet_name="schema")

# Index schema by site for easy lookup
schema_indexed = schema.set_index("site")

# 1) Fill Loop_IP for rt01 / rt02 / core
def get_loop(row):
    site = row["site"]
    dev = row["device"]
    if dev in ["rt01", "rt02", "core"]:
        return schema_indexed.loc[site, dev]
    return None

# 2) Fill mgmt_IP for switches (sw1, sw2, sw3...)
#    sw1 = schema.sw
#    sw2 = schema.sw with last octet +1
#    sw3 = schema.sw with last octet +2
def get_mgmt(row):
    if row["device"] == "sw" and not math.isnan(row["SW_num"]):
        site = row["site"]
        base_ip = schema_indexed.loc[site, "sw"]  # e.g., "10.1.4.1"
        parts = str(base_ip).split(".")
        if len(parts) == 4:
            try:
                last = int(parts[3])
                offset = int(row["SW_num"]) - 1   # SW_num=1 -> +0, SW_num=2 -> +1, etc.
                parts[3] = str(last + offset)
                return ".".join(parts)
            except Exception:
                # fallback: if something goes wrong, just return base_ip
                return base_ip
    return None

# Apply functions
device["Loop_IP"] = device.apply(get_loop, axis=1)
device["mgmt_IP"] = device.apply(get_mgmt, axis=1)

print(device)


with pd.ExcelWriter("IPschemaTest_v1_out.xlsx") as writer:
    device.to_excel(writer, sheet_name="device", index=False)
    schema.to_excel(writer, sheet_name="schema", index=False)
