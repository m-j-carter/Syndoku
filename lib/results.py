## This module includes all the methods required to save the results to a human-readable .txt file. 
## At a later date, this could be modified to write to an online database instead of a .txt file. 

## Written By: Michael Carter, Oct./Nov. 2019
## For my PSYCO 403/505 research project

# Notes/Changelog:
#    - I hope to add logging of any errors to the file at some point

import os
import random

LINEBREAK = "\n" + "-" * 80 + "\n"

class ResultsFile:
	# This class represents one .txt file of the results of one participant's trial. 
	# The file is named "results" + 3 random digits, e.g. "results123.txt".
	
	
	# For each trial, an info line must be written, signifying:
	#     1. number of words presented
	#     2. presentation time
	#     3. delay time
	#     4. whether or not the words were colored
	
	
	def __init__(self):
		self.__filename = self.__generate_unique_filename()
		self.__create_file()
	
	def __create_file(self):
		# touch the file to create it
		self.__file = open(self.__filename, 'x')
		self.__file.close()
			
	def __generate_unique_filename(self):
		filename = 'results%03d'%(random.randint(0,999))
		if os.path.exists('%s.txt'%(filename)):
			# try with another name	
			return self.__generate_unique_filename()
		else:
			return filename
		
	
	def new_trial_header(self, word_list, present_time, delay_time, colored=False):
		# initializes a new trial, writing the info header to the file.
		# word_list is in the actual order presented.
		with open(self.__filename, 'a') as file:
			file.write(LINEBREAK)
			file.write("Words (%d): %s\n" % (len(word_list), word_list))
			file.write("Presentation time: %d seconds\n" % (present_time))
			file.write("Delay time: %d seconds\n" % (delay_time))	
			file.write("Colored: %s\n" % (colored))
		file.close()

	def new_results_header(self, time_limit):
		# writes the relevant recall task info before the results.
		with open(self.__filename, 'a') as file:
			file.write("Time Limit: %.1f minutes\n" % (time_limit))
			file.write("------ Text --- Start -- End")
			file.write("\n")
		file.close()		
		
	def write_result(self, text, start_time, end_time):
		# writes one line of the participant's input to the file, along with their
		#   start and end time (corresponding to the first keypress until "enter" is pressed).
		# If an entry is invalid (i.e. NoneType), it is replaced by its type.
		with open(self.__filename, 'a') as file:		
			try:
				file.write("%11s\t" % (text))
				file.write("%.3f\t" % (start_time))
				file.write("%.3f\t" % (end_time))				
			except TypeError:
				file.write("None")	

			file.write("\n")
		file.close()
	