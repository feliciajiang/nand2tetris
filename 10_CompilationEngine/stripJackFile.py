import sys
import re


def stripJackFile(inputJackFile, outputJackFile):
	'''
	In: file name of the input Jack file, file name of the output Jack file 
	Out: writes a .jack file stripped of C-style comments
	Function: removes multi-line comments like /* */ or single line comments //
	'''
	in_comment = False

	with open(inputJackFile) as f:
		with open(outputJackFile, "w") as f1:

			for line in f:
				if '/*' in line:
					in_comment = True

				if '*/' in line: 
					in_comment = False
					line = line.split('*/')[1]

				# remove multiline comments (/*COMMENT */)
				line = re.sub(re.compile("/\*.*?\*/",re.DOTALL|re.MULTILINE) ,"" ,line)

				# remove singleline comments (//COMMENT\n )
				line = re.sub(re.compile("//.*?\n" ) ,"" ,line)

				if in_comment == True:
					line = ''
	
				# if line is not blank, write to outfile
				line = " ".join(line.split())
				if line != "":
					f1.write(line + "\n")



def testStrip(line):
	'''
	test function for stripJackFile
	'''
	
	# remove all occurance streamed comments (/*COMMENT */) from string
	line = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,line)
	# remove all occurance singleline comments (//COMMENT\n ) from string
	line = re.sub(re.compile("//.*?\n" ) ,"" ,line)
	# remove whitespace except between quotes 
	lst = line.split('"')
	for i, item in enumerate(lst):
		if not i % 2:
			lst[i] = re.sub("\s+", "", item)

	line = '"'.join(lst)
	
	return line
