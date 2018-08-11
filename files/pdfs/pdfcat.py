#!/usr/bin/env python

import sys
from PyPDF2 import PdfFileMerger


def pdf_cat(input_files, output_file):
    merger = PdfFileMerger()
    for pdf_file in input_files:
        merger.append(pdf_file)
    merger.write(output_file)


if __name__ == '__main__':
    pdf_cat(sys.argv[1:], '/tmp/output_file.pdf')
