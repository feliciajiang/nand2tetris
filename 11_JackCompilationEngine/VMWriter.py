import os 
import sys 
import CompilationEngine


class VMWriter:


	def __init__(self,outfileName):
		'''
		Creates a new file and prepares it for writing.
		'''

		# set buffersize to 0
		self.f1 = open(outfileName,'a', 0)


	def w(self, output):
		'''
		Helper function to write to output file 
		'''
		self.f1.write('%s' % output)


	def writePush(self,segment,index):
		'''
		In: segment (CONST,ARG, LOCAL,STATIC,THIS,THAT,POINTER,TEMP)
			Index
		Writes a VM push command
		'''
		self.w('push %s %s\n' % (segment, index))


	def writePop(self, segment, index):
		'''
		In: segment (CONST, ARG, LOCAL,STATIC,THIS,THAT,POINTER,TEMP)
			Index
		Writes a VM pop command
		'''
		self.w('pop %s %s\n' % (segment, index))


	def writeArithmetic(self, command):
		'''
		In: command (ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT)
		'''
		self.w('%s\n' % command)


	def writeLabel(self,label):
		'''
		Writes a VM label command.
		'''
		self.w('label %s\n' % label)


	def writeGoto(self,label):
		'''
		Writes a VM goto command.
		'''

		self.w('goto %s\n' % label)


	def writeIf(self,label):
		'''
		Writes a VM If command.
		'''
		self.w('if-goto %s\n' % label)


	def writeCall(self,name,nArgs):
		'''
		Writes a VM call command.
		'''
		self.w('call %s %s\n' % (name,nArgs))


	def writeFunction(self,name,nLocals):
		'''
		Writes a VM function command.
		'''
		self.w('function %s %s\n' % (name,nLocals))


	def writeReturn(self):
		'''
		Writes a VM return command.
		'''
		self.w('return\n')




