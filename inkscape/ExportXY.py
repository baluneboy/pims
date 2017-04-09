#!/usr/bin/env python

import inkex
import sys

class TemplateEffect(inkex.Effect):
	def __init__(self):
		# Call base class construtor.
		inkex.Effect.__init__(self)

	def effect(self):

		#Loop through all the selected items in Inkscape
		for node in self.selected.iteritems():

			#Create the string variable which will hold the formatted data (note that '\n' defines a line break)
			outputString = ""

			#Iterate through all the selected objects in Inkscape
			for id, node in self.selected.iteritems():
							#Check if the node is a path ( "svg:path" node in XML )
				if node.tag == inkex.addNS('path','svg'):

							#Create the string variable which will hold the formatted data (note that '\t' defines a tab space)
					outputString += ""

					#The 'd' attribute is where the path data is stored as a string
					pathData = node.get('d')

					#Split the string with the espace character, thus getting an array of the actual SVG commands
					pathData = pathData.split(' ')

					#Iterate through all the coordinates, ignoring the 'M' (Move To) and 'z' (Close Path) commands - note that any other command (such as bezier curves) will be unsupported and will likely make things go wrong
					for i in range( len(pathData)-1 ):
						#If there is a comma, we know that we are dealing with coordinates (format "X,Y") - ignoring any other SVG command (such as 'M', 'z', etc.)
						if pathData[i].find(',') >= 0:
							currentCoordinates = pathData[i].split(',')
							#Get the X and Y coordinates
							x = currentCoordinates[0]
							y = currentCoordinates[1]
							#Add them as a new 'vertice' node containing the coordinates as the 'x' and 'y' attributes

							outputString += str(x) + "," + str(y) + "\n"




			sys.stderr.write(outputString)

# Create effect instance and apply it.
effect = TemplateEffect()
effect.affect()
