#!/usr/bin/env python

import sys
import os
from mutagen.mp3 import MP3

def round_mp3_sec(mp3_file):
	audio = MP3(mp3_file)
	return int(round(audio.info.length))
	
def fit_to_dur(files, total_minutes=15.0):

	total_sec = int(round(total_minutes * 60.0))
	candidates = []
	fileSizes = []
	for name in files:
		try:
			size_round_sec = round_mp3_sec(name)
			fileSizes.append(size_round_sec)
			candidates.append([size_round_sec, name])
		except:
			print "Ignoring ", name
			continue

	print "Initial candidate list contained", len(fileSizes), "items..."
	print "Rounded file durations to fit in", total_minutes, "minutes were:", fileSizes, "(sec)."

	optimalResult = {}
	lastStep = {}
	for containerSize in xrange(0, total_sec+1):  # containerSize takes values 0 .. total_sec
		for idx,fileSize in enumerate(fileSizes):
			cellCurrent = (containerSize, idx)
			cellOnTheLeftOfCurrent = (containerSize, idx-1)
			if containerSize<fileSize:
				optimalResult[cellCurrent] = optimalResult.get(cellOnTheLeftOfCurrent,0)
				lastStep[cellCurrent] = lastStep.get(cellOnTheLeftOfCurrent,0)
			else:
				# If I use file of column "idx", then the remaining space is...
				remainingSpace = containerSize - fileSize
				# ...and for that remaining space, the optimal result using the first idx-1 columns was:
				optimalResultOfRemainingSpace = optimalResult.get((remainingSpace, idx-1),0)
				if optimalResultOfRemainingSpace + fileSize > optimalResult.get(cellOnTheLeftOfCurrent,0):
					# we improved the best result, using the column "idx"!
					optimalResult[cellCurrent] = optimalResultOfRemainingSpace + fileSize
					lastStep[cellCurrent] = fileSize
				else:
					# no improvement...
					optimalResult[cellCurrent] = optimalResult[cellOnTheLeftOfCurrent]
					lastStep[cellCurrent] = lastStep.get(cellOnTheLeftOfCurrent,0)

	finalChosenList = []
	print "Attainable:", optimalResult[(total_sec, len(fileSizes)-1)] / 60.0, "minutes"
	print "Attainable:", optimalResult[(total_sec, len(fileSizes)-1)], "seconds"
	total = optimalResult[(total_sec, len(fileSizes)-1)]
	countingUp = 0
	while total>0:
		lastFileSize = lastStep[(total, len(fileSizes)-1)]
		# print total, "removing", lastFileSize
		if lastFileSize != 0:
			for pair in candidates:
				if pair[0] == lastFileSize:
					finalChosenList.append(pair[1])
					countingUp += lastFileSize
					print "+ %9d sec = %9d sec (%s)" % (lastFileSize, countingUp, pair[1])
					candidates.remove(pair)
					break
			else:
				assert(False) # we should have found the file
		total -= lastFileSize
	return finalChosenList
