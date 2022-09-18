"""
Usage: sort.py <path_to_file>

Sorts all entries in file based on Totalindex
"""
import os.path
import sys

import pandas as pd


def sort(data_frame):
    data_frame.sort_values(["Totalindex"], ascending=True, inplace=True)


if __name__ == "__main__":
    file = sys.argv[1]

    if ".csv" in file:
        df = pd.read_csv(file)
        sort(df)
        df.to_csv(file)

    elif ".json" in file:
        df = pd.read_json(file)
        sort(df)
        df.to_json(file)

    else:
        ext = os.path.splitext(file)[1]
        print(f"Unsupported filetype {ext}")
        sys.exit(1)

    print(f"Sorted {file}")
    sys.exit(0)
