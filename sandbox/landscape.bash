#!/usr/bin/env bash

PLOT1x1=${1}
LANDTMP=${2}
TMPOUT=${PLOT1x1/.pdf}_scale_0p66_offset_n1p5in_0p15in.pdf
PDFOUT=${PLOT1x1/.pdf}_nopagenum.pdf

# get matlab plot_1x1 scaled and offset for overlaying onto portrait handbook templated PDF
pdfjam --papersize '{11in,8.5in}' --scale 0.66 --offset '-1.5in 0.15in' ${PLOT1x1} --outfile ${TMPOUT}
pdftk ${TMPOUT} background ${LANDTMP} output ${PDFOUT}
rm ${TMPOUT}
