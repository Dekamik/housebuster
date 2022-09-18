"""
Usage: sort.py <path_to_file>

Sorts all entries in file based on Totalindex
"""
import sys

import pandas as pd


def sort_json(file_path):
    df = pd.read_json(file_path)
    df.sort_values(["Totalindex"], ascending=True, inplace=True)
    df.to_json(file_path)


def sort_csv(file_path):
    df = pd.read_csv(file_path)
    df.sort_values(["Totalindex"], ascending=True, inplace=True)
    df.to_csv(file_path)


if __name__ == "__main__":
    file = sys.argv[1]

    if ".csv" in file:
        sort_csv(file)

    elif ".json" in file:
        sort_json(file)

    sys.exit(0)
