import JackTokenizer as JT
import CompilationEngine as CE
import os
import sys 


def tokenizeAndCompile(filename):
	'''
	In: .jack file 
	Out: xxx.xml file, xxx.vm file 
	Function: handles parsing the names of all the files
	calls JackTokenizer object to create T.xml file 
	then calls CompilationEngine to create .xml file 
	'''

	# get outfileName ('T.xml')
	ToutfileName = os.path.abspath(filename).split('.')[0] + "T.xml"
	if os.path.isfile(ToutfileName): os.remove(ToutfileName)
	
	tokObj = JT.JackTokenizer(os.path.abspath(filename), ToutfileName)
	tokObj.tokenize()
	tokArray = tokObj.getTokenizedList()

	# remove xxxT.xml file - we needed it for Project 10, but not anymore 
	outfileTName = os.path.abspath(filename).split('.')[0] + "T.xml"
	if os.path.isfile(outfileTName): os.remove(outfileTName)	

	# get outfileName (name of the final .xml file)
	outfileName = os.path.abspath(filename).split('.')[0] + ".xml"
	if os.path.isfile(outfileName): os.remove(outfileName)

	# get outfileName (name of the final .vm file)
	outVMName = os.path.abspath(filename).split('.')[0] + ".vm"
	if os.path.isfile(outVMName): os.remove(outVMName)
	
	# inputs to CompilationEngine are JackTokenizerOutput array and outfileName
	c = CE.CompilationEngine(tokArray, outfileName, outVMName)
	c.compileClass()


def main():
	'''
	Calls tokenizeAndCompile, and handles file versus folder inputs.
	'''

	# command line parsing: format should be > python JackAnalyzer.py folderorfile/name/
	commands = [arg for arg in sys.argv[1:]]

	if len(commands) > 1:
		print("Wrong command line inputs.")
		sys.exit(0)
	else:
		inputF = commands[0]


	# handle case when inputfile is just one file 
	if os.path.isfile(inputF):
		tokenizeAndCompile(inputF)

	# handle case when inputfile is a folder
	if os.path.isdir(inputF):

		# iterate through each file in inputF and check if it is a jack file 
		for filename in os.listdir(inputF):
			if filename.endswith('.jack'): 
				abspath = os.path.join(os.path.abspath(inputF), filename)
				tokenizeAndCompile(abspath)


main()
