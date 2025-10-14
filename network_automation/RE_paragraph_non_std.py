import re
import pandas as pd

# --- helpers ---
BLOCK_START = re.compile(r'(?im)^tacacs\s+server\b')  # start of each tacacs block
HAS_10_ADDR = re.compile(r'(?im)^\s*address\s+ipv4\s+10(?:\.\d{1,3}){3}\b')  # an address line in 10.x.x.x
KEY_LINE     = re.compile(r'(?im)^\s*(key\s+7\s+[^\r\n]+)')  # whole "key 7 ..." line
# If you only want the value after 'key 7', use: re.compile(r'(?im)^\s*key\s+7\s+([^\r\n]+)')

def normalize_newlines(s: str) -> str:
    """Turn literal '\\n' or '\\r\\n' sequences into real newlines; unify newlines; strip odd spaces."""
    if s is None:
        return ""
    s = str(s)
    # Convert escaped sequences to real newlines (common when exports store '\n' textually)
    s = s.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\r\n', '\n')
    # Normalize non-breaking spaces etc.
    s = s.replace('\xa0', ' ').replace('\u3000', ' ')
    return s

def split_tacacs_blocks(s: str):
    """Yield each block starting at 'tacacs server ...' up to next 'tacacs server' or end."""
    s = normalize_newlines(s)
    # Find all start indices
    starts = [m.start() for m in BLOCK_START.finditer(s)]
    if not starts:
        return []
    starts.append(len(s))  # sentinel for the last slice
    return [s[starts[i]:starts[i+1]] for i in range(len(starts)-1)]

def extract_keys_from_cell(text: str):
    """From a multi-line cell: extract 'key 7 ...' lines only from blocks that have address 10.x.x.x"""
    blocks = split_tacacs_blocks(text)
    keys = []
    for blk in blocks:
        if HAS_10_ADDR.search(blk):              # enforce your “address ipv4 10.x.x.x present” rule
            keys.extend(KEY_LINE.findall(blk))   # collect all key lines within this block
    return "; ".join(keys) if keys else None
