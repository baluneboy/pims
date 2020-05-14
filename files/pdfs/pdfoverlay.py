# !/usr/bin/python
# Adding a watermark to a single-page PDF

import os
import PyPDF2
from pathlib import Path


def apply_watermark(input_file, output_file, watermark_file="c:/temp/watermark.pdf"):
    """overlay watermark on input file and save new output file"""

    with open(input_file, "rb") as filehandle_input:
        # read content of the original file
        pdf = PyPDF2.PdfFileReader(filehandle_input)

        with open(watermark_file, "rb") as filehandle_watermark:
            # read content of the watermark
            watermark = PyPDF2.PdfFileReader(filehandle_watermark)

            # get first page of the original PDF
            first_page = pdf.getPage(0)

            # get first page of the watermark PDF
            first_page_watermark = watermark.getPage(0)

            # merge the two pages
            first_page.mergePage(first_page_watermark)

            # create a pdf writer object for the output file
            pdf_writer = PyPDF2.PdfFileWriter()

            # add page
            pdf_writer.addPage(first_page)

            with open(output_file, "wb") as filehandle_output:
                # write the watermarked file to the new file
                pdf_writer.write(filehandle_output)


def main(top_dir):
    p = Path(top_dir)
    sorted_files = sorted(list(p.glob('20*_cutemps_er6locker3aggcurrent.pdf')))
    for f in sorted_files:
        input_file = str(f)
        output_file = input_file.replace('er6locker3', 'er6locker1')
        apply_watermark(input_file, output_file)
        print(output_file)


if __name__ == '__main__':
    top_dir = os.sep.join(['d:', 'cutemps_cache'])
    main(top_dir)
