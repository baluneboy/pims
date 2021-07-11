#!/usr/bin/env python

import sys
import csv
from itertools import izip


def readall_transpose_write(csv_in, csv_out):
    a = izip(*csv.reader(open(csv_in, "rb")))
    csv.writer(open(csv_out, "wb")).writerows(a)


if __name__ == "__main__":
    csv_in = sys.argv[1]
    csv_out = csv_in.replace(".csv", "_transposed.csv")
    readall_transpose_write(csv_in, csv_out)
