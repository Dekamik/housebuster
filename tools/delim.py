#!/usr/bin/env python3
"""
Usage: delim.py <csv_file> <old_delimiter> <new_delimiter>

Changes delimiter on CSV files.
"""
import sys

import pandas as pd


file = sys.argv[1]
old_delim = sys.argv[2]
new_delim = sys.argv[3]


df = pd.read_csv(file, sep=old_delim)
df.to_csv(file, sep=new_delim, index=False)
