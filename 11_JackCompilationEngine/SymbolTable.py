import sys
import os 
import re


'''
- the identifier category (var, argument, static, field, class, subroutine);

-whether the identifier is presently being defined (e.g., the identifier 
stands for a variable declared in a var statement) or used (e.g., the 
identifier stands for a variable in an expression);

- whether the identifier represents a variable of one of the four kinds 
(var, argument, static, field ), and the running index assigned to the 
identifier by the symbol table.



We pick the output of the XML to be 
if declared, like static, field, or var: 
	<identifier> declared/used name type kind index </identifier>

if in argument list:
	<identifier> name type(argument) kind index </identifier>

if class name:
	<identifier> class ClassName </identifier>

if subroutine name: 
	<identifier> subroutine subroutineName </identifier>

'''

class SymbolTable:

	def __init__(self):
		#self.subScope = {}
		# first item is subroutine symbol table, second item is class symbol Table
		self.scope = [{},{}]

		# when we start off building the symbol table, we add stuff to the class
		# scope first which is at index 1 
		self.curScope = 1

		self.curKind = ''			# this is static, field, var, etc
		self.curType = ''			# this is int, string, or boolean
		self.curIndex = 0

	def setType(self,newCurType):
		'''
		Sets type.
		'''
		self.curType = newCurType


	def setKind(self,newCurKind):
		'''
		Sets kind.
		'''
		self.curKind = newCurKind


	def startSubroutine(self):
		'''
		Starts a new subroutine scope, ie reset dictionary for subroutine.
		'''

		self.scope[0] = {}
		self.curScope = 0


	def define(self,name):
		'''
		In: name (String) type (String) kind (STATIC, FIELD, ARG, or VAR)
		Defines a new identifier of a given name, type, and kind and assigns 
		it a running index. STATIC and FIELD identifiers have a class scope, 
		while ARG and VAR identifiers have a subroutine scope.
		'name': [type,kind,index]
		'''

		self.curIndex = self.varCount(self.curKind)

		self.scope[self.curScope][name] = [self.curType,self.curKind,self.curIndex]

		print '\n'+name 		# testing purposes
		for item in self.scope[self.curScope][name]:
			print item


	def varCount(self,kind):
		'''
		In: kind (STATIC, FIELD, ARG, or VAR)
		Out: int
		Returns the number of variables of the given kind already defined in the 
		current scope.
		'''
		count = 0

		# search class scope for field variables so that we can allocate
		# the correct amount of memory using Memory.alloc
		if kind == 'field':
			for name in self.scope[1]:
				if kind == self.scope[1][name][1]:
					count+=1 

		# otherwise, look at current scope (usually method scope)
		else:
			for name in self.scope[self.curScope]:
				if kind == self.scope[self.curScope][name][1]:
					count += 1

		return count


	def kindOf(self,name):
		'''
		Returns the kind of the named identifier in the current scope. 
		If the identifier is unknown in the current scope, returns NONE.
		'''
		if name in self.scope[self.curScope]:
			return self.scope[self.curScope][name][1]

		else:

			# if we cant find an identifier in scope 0 (method scope), try scope 1 (class scope)
			self.curScope = 1

			if name in self.scope[self.curScope]:
				temp = self.scope[self.curScope][name][1]
				self.curScope = 0 							# reset to method scope 
				return temp
			
			# if we can't find it in class scope either, it must just be a class name 
			else:
				self.curScope = 0							# reset to method scope 
				return None


	def typeOf(self,name):
		'''
		In: name (String)
		Out: string
		Returns the type of the named identifier in the current scope.
		'''
		if name in self.scope[self.curScope]:
			return self.scope[self.curScope][name][0]

		else:

			# if we cant find an identifier in scope 0 (method scope), try scope 1 (class scope)
			self.curScope = 1

			if name in self.scope[self.curScope]:
				temp = self.scope[self.curScope][name][0]
				self.curScope = 0 							# reset to method scope 
				return temp
			
			# if we can't find it in class scope either, it must just be a class name 
			else:
				self.curScope = 0							# reset to method scope 
				return None



	def indexOf(self,name):
		'''
		In: name (String)
		Out: int
		Returns the index assigned to the named identifier.
		'''
		if name in self.scope[self.curScope]:
			return str(self.scope[self.curScope][name][2])

		else:

			# if we cant find an identifier in scope 0 (method scope), try scope 1 (class scope)
			self.curScope = 1

			if name in self.scope[self.curScope]:
				temp = self.scope[self.curScope][name][2]
				self.curScope = 0 							# reset to method scope 
				return str(temp)
			
			# if we can't find it in class scope either, it must just be a class name 
			else:
				self.curScope = 0							# reset to method scope 
				return None



	def returnAttr(self,name):
		'''
		Helper function to print information about identifiers in XML output 
		returns string: 'identifierName kind(var,field,etc) type index'
		'''
		if name in self.scope[self.curScope]:
			return name + ' ' + self.kindOf(name) + ' ' + self.typeOf(name) + ' ' + self.indexOf(name)

		else:
			# if we cant find an identifier in scope 0, try class scope 1
			self.curScope = 1

			if name in self.scope[self.curScope]:
				temp = name + ' ' + self.kindOf(name) + ' ' + self.typeOf(name) + ' ' + self.indexOf(name)

				# reset curScope to 0 which is subroutine 
				self.curScope = 0 
				return temp

			

