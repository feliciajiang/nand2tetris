import stripJackFile as s
import JackTokenizer as jt
import os
import SymbolTable as st
import VMWriter as vmw


class CompilationEngine:

	ops = [ '+' , '*' , '/' , '-'
		, '&' , '|',',' ,'<' , '>' , '=' 
		, '&lt;', '&gt;', '&quot;', '&amp;']

	unaryOps = ['~','-']

	vmKind = {'argument': 'argument', 
			'static': 'static',
			'variable': 'local',
			'field': 'this'}

	vmOps = {
			'+': 'add',
			'-': 'sub',
			'=': 'eq',
			'&gt;': 'gt',
			'&lt;': 'lt',
			'&amp;': 'and',
			'|': 'or'
			}

	vmUnaryOps = {
			'-': 'neg',
			'~': 'not'
			}
	    
    
	def __init__(self,jackTokenizerOutput,outfileName,outVMName):
		'''
		In: jackTokenizerOutput which is the array of tokens output by JackTokenizer.py
		Function: Creates a new compilation engine with the given input and output. 
		The next routine called must be compileClass().
		'''

		self.tokenArray = jackTokenizerOutput
		self.tokenIndex = 0
		self.line = self.tokenArray[0]		# first item of array is class

		self.curToken = self.line.split()[1] # the second item in a line is the token

		self.curTokenType = self.line.split()[0]	# gets the first tag of the token 
		
		# set buffersize to 0
		self.f1 = open(outfileName,'a', 0)


		# project 11 part: add Symbol table and VMWriter output 
		self.sTable = st.SymbolTable()
		self.vm = vmw.VMWriter(outVMName)

		# project 11 class variables
		self.curClass = ''							# name of the current class 
		self.whileCount = 0
		self.ifCount = 0


	def testReadLine(self):
		'''
		Test function to check that line incrementing is working 
		'''
		print 'Line is: ' + self.line
		print 'Token is: ' + self.curToken


	def nextToken(self):
		'''
		Reads next line in inputFile and advances next token 
		'''
		# increment token Array Index
		self.tokenIndex += 1
		self.line = self.tokenArray[self.tokenIndex]

		if len(self.line.split()) == 1:
			self.curToken = self.line

		# case when its <something> token </something>
		elif len(self.line.split()) == 3:
			self.curToken = self.line.split()[1] # the second item in a line is the token
			self.curTokenType = self.line.split()[0]

		# case when its <stringConstant> here is my string </stringConstant>
		else:
			self.curToken = ' '.join(self.line.split(' ')[1:-1])
			self.curTokenType = self.line.split()[0]


	def w(self, output):
		'''
		Helper function to write to output .xml file 
		'''
		self.f1.write('%s' % output)


	def compileClass(self):
		'''
		Compiles a complete class. Called when keyword Class is detected.
		'''
		# class grammer: Class -> keyword, Main/etc -> identifier, { -> symbol, subroutineDec

		self.w('<class>\n')
		self.w(self.line)		# <keyword> class </keyword>
		
		self.nextToken()		# <identifier> Main </identifier> (or some other identifier)
		self.w('<identifier> class ' + self.curToken + ' </identifier>\n')

		# set curClass to the latest class that we are compiling 
		self.curClass = self.curToken

		self.nextToken()
		self.w(self.line)		# <symbol> { </symbol> 

		self.nextToken()			# always enter another compileFunction with next token

		while self.curToken:

			if self.curToken in ['static','field']:
				self.compileClassVarDec()

			elif self.curToken in ['constructor','function','method']:
				self.compileSubroutine()

			elif self.curToken == '}':
				self.w(self.line)
				self.w('</class>\n')	# end class declaration section
				self.nextToken()
				
			else: 
				if self.curToken == '</tokens>':
					self.f1.close()
					return


	def compileClassVarDec(self):
		'''
		Compiles a static declaration or a field declaration.
		'''
		# start classVarDec section
		self.w('<classVarDec>\n')

		# curToken when we enter compileClassVar is static or field 
		self.w(self.line) 			# <keyword> field or static </keyword>
		self.sTable.setKind(self.curToken)

		self.nextToken()			# this should be a type 
		self.w(self.line)			# <keyword> void, int, char, boolean, classname  </keyword>
		self.sTable.setType(self.curToken)


		while self.curToken != ';': 
			self.nextToken()
	
			# add class variable declarations to symbol table 
			if self.curToken not in [',',';']:
				self.sTable.define(self.curToken)
				self.w('<identifier> declared ' + self.sTable.returnAttr(self.curToken) + ' </identifier>\n')


			else:
				self.w(self.line)

		# when we exit this while loop, self.curToken = ';'

		self.w('</classVarDec>\n')	# end classVarDec section 
		self.nextToken()			# advance to next token before returning
		
		return 


	def compileSubroutine(self):
		'''
		Compiles a complete method, function, or constructor.
		'''
		# start new subroutine in SymbolTable
		self.sTable.startSubroutine()		

		# start subroutineDeclaration section
		self.w('<subroutineDec>\n')

		# curToken when we enter compileClassVar is constructor, function, or method
		self.w(self.line)				# <keyword> constructor, function, or method </keyword>
		subroutineKind = self.curToken 	# save whether this is constructor, function, or method 

		if self.curToken == 'constructor' or self.curToken == 'function':

			self.nextToken()		# Class name  
			self.w('<identifier> class ' + self.curToken + ' </identifier>\n') 

		# case when curToken = method or function
		else:

			# add itself to the symbol table 
			# 'this ClassName argument 0' as the first line of the method-scope STable 
			self.sTable.setKind('argument')
			self.sTable.setType(self.curClass)
			self.sTable.define('this')

			self.nextToken()		# type 
			self.w(self.line)		# void, int, char, boolean, or className 		


		self.nextToken()		# subroutineName identifier
		self.w('<identifier> subroutine ' + self.curToken + ' </identifier>\n')
		subroutineName = self.curToken


		self.nextToken()		# '(' 
		self.w(self.line)

		self.nextToken()		# curToken is first parameter ( or ')' )
		self.compileParameterList()


		# when we exit compileParameterList, curToken is last parenthesis ')'
		self.w(self.line)


		# start subroutineBody section
		self.w('<subroutineBody>\n')

		self.nextToken()		# this is the first curly brace '{'
		self.w(self.line)

		# curToken when we enter compileClassVar is 'var'
		self.nextToken()

		while self.curToken == 'var':
			self.compileVarDec()


		# write function out to VM file after getting parameters and local var parameters 
		# but before compiling statements
		funcName = '%s.%s' % (self.curClass, subroutineName)
		numLocals = self.sTable.varCount('variable')
		self.vm.writeFunction(funcName, numLocals)


		if subroutineKind == 'constructor':
			numFields = self.sTable.varCount('field')
			self.vm.writePush('constant', numFields)
			self.vm.writeCall('Memory.alloc', 1)
			self.vm.writePop('pointer', 0)

		if subroutineKind == 'method':
			self.vm.writePush('argument', 0)
			self.vm.writePop('pointer', 0)


		while self.curToken:				

			if self.curToken in ['let', 'if', 'else', 'while', 'do', 'return']:
				self.compileStatements()
				# when we exit out of compileStatements, curToken = '}'

			else:

				#if self.curToken == '}':
				self.w(self.line)
				# end subroutineBody section
				self.w('</subroutineBody>\n')
				# end subroutineDec section
				self.w('</subroutineDec>\n')
				self.nextToken()
				return


	def compileParameterList(self):
		'''
		Compiles a (possibly empty) parameter list, not including the enclosing "()"
		'''
		# set current type of symbol to argument in Symbol Table
		self.sTable.setKind('argument')

		# start parameterList section, even if list is empty (ie '()')
		self.w('<parameterList>\n')

		while self.curToken:

			# if curToken is ending parenthesis ')', end parameterList section 
			# and exit out of compileParameterList without printing parenthesis
			if self.curToken == ')':
				self.w('</parameterList>\n')
				return

			# If curToken is not parenthesis, assume parameters are correct.
			# Print to outfile, and advance token
			else:

				# add argument symbol to symbol Table
				if self.curToken in ['int','String','boolean','Array']:
					self.sTable.setType(self.curToken)
					self.w(self.line)

				elif self.curToken == ',':
					self.w(self.line)

				else:
					#if self.curToken != ',':
					self.sTable.define(self.curToken)
					self.w('<identifier> ' + self.sTable.returnAttr(self.curToken) + ' </identifier>\n')

				self.nextToken()



	def compileVarDec(self):
		'''
		Compiles a var declaration.
		'''
		self.sTable.setKind('variable')		# "local" or "variable"?
		# curToken is 'var' when we enter this function 
		# start varDeclaration section
		self.w('<varDec>\n')

		self.w(self.line)	# 'var'

		self.nextToken()	# type: 'void', int', 'char', 'boolean' or className
		self.w(self.line)

		self.sTable.setType(self.curToken)

		self.nextToken()

		while self.curToken:
			if self.curToken == ';':
				self.w(self.line)
				# end varDeclaration section 
				self.w('</varDec>\n')
				self.nextToken()
				return

			else:
				if self.curToken != ',':
					self.sTable.define(self.curToken)
					self.w('<identifier> declared ' + self.sTable.returnAttr(self.curToken) + ' </identifier>\n')

				else:
					self.w(self.line)

				self.nextToken()


	def compileStatements(self):
		'''
		Compiles a sequence of statements, not including the enclosing "{}".
		'''
		self.w('<statements>\n')

		# curToken is 'let', 'if', 'else', 'while', 'do', 'return'  
		# when we enter this function 

		while self.curToken:

			if self.curToken == 'do':
				self.compileDo()

			elif self.curToken == 'let':
				self.compileLet()

			elif self.curToken == 'while':
				self.compileWhile()

			elif self.curToken == 'return':
				self.compileReturn()

			elif self.curToken == 'if':
					self.compileIf()
			
			else:	#if self.curToken == '}':
				self.w('</statements>\n')
				return


	def compileDo(self):
		'''
		Compiles a do statement.
		'''
		# curToken = 'do' when we enter this function
		self.w('<doStatement>\n')

		self.w(self.line) 			# 'do'
		self.nextToken()			# identifier (e.g. 'draw')

		# when we enter compileSubroutineCall, curToken is an identifier
		self.compileSubroutineCall()
		self.vm.writePop('temp', 0)			# this is to get rid of returned 0's?

		self.w('</doStatement>\n')
		self.nextToken()


	def compileSubroutineCall(self):
		'''
		Helper function to compile calls to subroutines. Take the form 
			subroutineName (expressionlist)
		or 
			className.subroutineName(expressionlist)
		or 
			varName.subroutineName(expressionList)
		'''

		self.w('<identifier> subroutine ' + self.curToken + ' </identifier>\n')
		subroutineName1 = self.curToken


		# account for cases of subroutine call like 'Memory.dealloc'
		self.nextToken()
		if self.curToken == '.':
			self.w(self.line)		# '.'
			self.nextToken()		# subroutineName
			self.w('<identifier> subroutine ' + self.curToken + ' </identifier>\n')
			subroutineName2 = self.curToken

			# if it is xxx.subroutineName, then check what kind xxx is 
			typeOfIdentifier = self.sTable.typeOf(subroutineName1)

			# if we do not find xxx in symbol table, then xxx is a class
			# case when: className.subroutineName(expressionlist)
			if typeOfIdentifier == None:
				functionName = '%s.%s' %(subroutineName1,subroutineName2)
				numArgs = 0			# numArgs = 0 because functions have k arguments 

			# if we find xxx in symbol table, then xxx is an instance of a class
			# case when: varName.subroutineName(expressionList)
			else:
				objectKind = CompilationEngine.vmKind[self.sTable.kindOf(subroutineName1)]
				objectIndex = self.sTable.indexOf(subroutineName1)

				# push the object to the stack 
				self.vm.writePush(objectKind, objectIndex)
				functionName = '%s.%s' %(typeOfIdentifier,subroutineName2)
				#functionName = '%s.%s' %(subroutineName1,subroutineName2)
				numArgs = 1

			self.nextToken()

		# case when: subroutineName(expressionlist)
		else:
			functionName = '%s.%s' %(self.curClass,subroutineName1)
			numArgs = 1 
			self.vm.writePush('pointer', 0)


		self.w(self.line)			# '('

		self.nextToken()
		numArgs += self.compileExpressionList()

		# when we exit compileExpressionList, curToken = ')'
		self.w(self.line)			# ')'

		self.nextToken()
		self.w(self.line)			# ';'

		self.vm.writeCall(functionName, numArgs)



	def compileLet(self):
		'''
		Compiles a let statement.
		'''
		# curToken = 'let' when we enter this function
		self.w('<letStatement>\n')
		self.w(self.line)			# 'let'
		
		self.nextToken()			# varName identifier
		self.w('<identifier> used ' + self.sTable.returnAttr(self.curToken) + ' </identifier>\n')
		
		# get information about the variable at hand
		varName = self.curToken
		varKind = CompilationEngine.vmKind[self.sTable.kindOf(varName)]
		varIndex = self.sTable.indexOf(varName)

		self.nextToken()			

		# if we have brackets, like a[i], then expression in index
		if self.curToken == '[':
			self.w(self.line)		# '['

			self.nextToken()
			self.compileExpression()

			# when we exit out of compileExpression, curToken = ']'
			self.w(self.line)		# ']'

			# 1) push the array variable to the stack
			# 2) add the array variable address and the value in the expression 
			#		(which was pushed to stack in compileExpression)
			# 3) pop address to pointer 1, which sets the 'that' segment 
			# to the value in the array[xxx]
			self.vm.writePush(varKind, varIndex)
			self.vm.writeArithmetic('add')
			self.vm.writePop('pointer',1)  	#works

			self.nextToken()

			# next line is '='
			self.w(self.line)			# '='

			self.nextToken()
			self.compileExpression()

			self.w(self.line)			# ';'

			self.w('</letStatement>\n')
			self.nextToken()

			# pop whatever value was returned in the compileExpression
			# to the 'that' segment, which is currently set to the memory of 
			# array[xxx]
			self.vm.writePop('that', 0) # works 


		else: 
			# next line is '='
			self.w(self.line)			# '='

			self.nextToken()
			self.compileExpression()

			self.w(self.line)			# ';'

			self.w('</letStatement>\n')
			self.nextToken()

			self.vm.writePop(varKind, varIndex)



	def compileWhile(self):
		'''
		Compiles a while statement.
		'''
		# curToken = 'while' when we enter this function

		self.w('<whileStatement>\n')
		self.w(self.line)			# 'while'

		# create unique label for while loop 
		self.whileCount += 1 
		localWhileCount = str(self.whileCount)
		self.vm.writeLabel('StartWhile%s' % localWhileCount)

		self.nextToken()
		self.w(self.line)			# '('

		# no expression in this version yet 
		self.nextToken()
		self.compileExpression()
		self.vm.writeArithmetic('not') # eval false condition first

		self.w(self.line)			# ')' 		

		self.nextToken()
		self.w(self.line)			# '{' 


		# label to skip while loop, we already pushed conditions to stack in CompileExpression
		self.vm.writeIf('EndWhile%s' % localWhileCount)


		self.nextToken()
		self.compileStatements()
		# when we exit out of compileStatements, curToken = '}'

		self.w(self.line)			# '}'
		self.w('</whileStatement>\n')
		self.nextToken()

		self.vm.writeGoto('StartWhile%s' % localWhileCount)
		self.vm.writeLabel('EndWhile%s' % localWhileCount)



	def compileReturn(self):
		'''
		Compiles a return statement.
		''' 
		# curToken = 'return' when we enter this function
		self.w('<returnStatement>\n')

		self.w(self.line)				# 'return'

		self.nextToken()

		# if function type is void, push 0 to stack
		if self.curToken == ';':
			self.w(self.line)			# ';' if 'return;'
			self.vm.writePush('constant', 0)

		else:
			self.compileExpression()	# expression stuff
			self.w(self.line)			# ';'


		self.w('</returnStatement>\n')
		self.nextToken()

		self.vm.writeReturn()



	def compileIf(self):
		'''
		Compiles an if statement, possibly with a trailing else clause.
		'''
		# curToken = 'if' when we enter this function

		self.ifCount += 1
		localIfCount = str(self.ifCount)

		self.w('<ifStatement>\n')
		self.w(self.line)			# 'if'

		self.nextToken()
		self.w(self.line)			# '('

		# no expression in this version yet 
		self.nextToken()
		self.compileExpression()	

		self.w(self.line)			# ')' 		

		self.nextToken()
		self.w(self.line)			# '{' 

		self.vm.writeIf('True%s' % localIfCount)
		self.vm.writeGoto('False%s' % localIfCount)
		self.vm.writeLabel('True%s' % localIfCount)		

		self.nextToken()
		self.compileStatements()
		# when we exit out of compileStatements, curToken = '}'

		self.vm.writeGoto('End%s' % localIfCount)

		self.w(self.line)			# '}'
		self.nextToken()

		self.vm.writeLabel('False%s' % localIfCount)

		if self.curToken == 'else':
			self.w(self.line)			# 'else'

			self.nextToken()
			self.w(self.line)			# '{'

			self.nextToken()
			self.compileStatements()
			# when we exit out of compileStatements, curToken = '}'

			self.w(self.line)			# '}'
			self.nextToken()

		self.w('</ifStatement>\n')

		self.vm.writeLabel('End%s' % localIfCount)


	def compileExpression(self):
		'''
		Compiles an expression.
		'''
		# when we enter compileExpression, curToken is first token
		# of an expression or '('

		self.w('<expression>\n')


		while self.curToken:

			lookBack = self.tokenArray[self.tokenIndex - 1].split()[1]

			if self.curToken in [';' , ')' , ']' , ',']:
				self.w('</expression>\n')
				# when exit compileExpression, curToken = ';' or ')' or ']'
				return

				# case when: unary operator '-' or '~'
			elif self.curToken in CompilationEngine.unaryOps and lookBack in ['(',',']:
				self.compileTerm()
				# curToken = ??? when we exit compileTerm for something like 
				# let i = i + (-x);


			elif self.curToken in CompilationEngine.ops:
				op = self.curToken
				self.w(self.line)		# some operator like +, -, *, >, <
				self.nextToken()

				self.compileTerm()

				if op == '*':
					self.vm.writeCall('Math.multiply',2)

				elif op == '/':
					self.vm.writeCall('Math.divide',2)

				else:
					operator = CompilationEngine.vmOps[op]
					self.vm.writeArithmetic(operator)



			else:
				self.compileTerm()
				
		# when we exit compileExpression, curToken = ',' or ')' or ';'


	def compileTerm(self):
		'''
		Compiles a term. This routine is faced with a slight difficulty when 
		trying to decide between some of the alternative parsing rules. 
		Specifically, if the current token is an identifier, the routine must 
		distinguish between a variable, an array entry, and a subroutine call. 
		A single look ahead token, which may be one of "[", "(", or "." 
		suffices to distinguish between the three possibilities. Any other 
		token is not part of this term and should not be advanced over.
		'''

		self.w('<term>\n')					# start term section

		if self.curTokenType == '<integerConstant>':
			self.w(self.line)				# int constant
			self.w('</term>\n')

			self.vm.writePush('constant', self.curToken)

			self.nextToken()
			return

		elif self.curTokenType == '<stringConstant>':
			self.w(self.line)				# str constant
			self.w('</term>\n')

			# compile string using provided VM's 
			# initiate a string of correct length using String.new
			line = self.curToken
			self.vm.writePush('constant', len(line))
			self.vm.writeCall('String.new', 1)

			for c in line:
				self.vm.writePush('constant',ord(c))		# do i need ord(c)?
				self.vm.writeCall('String.appendChar', 2)


			self.nextToken()
			return


		elif self.curToken in ['true','false','null','this']:
			self.w(self.line)				# keyword true false or null
			self.w('</term>\n')

			# only this is pushed to pointer segment (address)
			# everything else goes to CONST
			if self.curToken == 'this':
				self.vm.writePush('pointer', 0)

			elif self.curToken == 'true':
				self.vm.writePush('constant', 0)
				self.vm.writeArithmetic('not')

			else:	# if 'null' or 'false'
				self.vm.writePush('constant', 0)
				
			self.nextToken()
			return	

		elif self.curToken in ['-','~']:
			self.w(self.line)				# '-' or '~'
			op = CompilationEngine.vmUnaryOps[self.curToken]

			self.nextToken()
			self.compileTerm()

			self.w('</term>\n')

			self.vm.writeArithmetic(op)

			return			


		elif self.curToken == '(':
			self.w(self.line)				# '('

			self.nextToken()
			self.compileExpression()
			# when we exit compileExpression, curToken = ')'

			self.w(self.line)				# ')'
			self.w('</term>\n')				# close term section
			self.nextToken()
			return
	

		elif self.curTokenType == '<identifier>':
			lookAhead = self.tokenArray[self.tokenIndex + 1].split()[1]


			# case when its an array: varName[expression]
			if lookAhead == '[':

				identifier = self.curToken # varName
				kind = self.sTable.kindOf(identifier)
				index = self.sTable.indexOf(identifier)
				self.vm.writePush(CompilationEngine.vmKind[kind], index)

				# identifier here
				self.w('<identifier> used ' + self.sTable.returnAttr(self.curToken) + ' </identifier>\n')

				# save state of current THAT pointer
				self.vm.writePush('pointer',1)
				self.vm.writePop('temp',0)

				self.nextToken()
				self.w(self.line)			# '['

				self.nextToken()
				self.compileExpression()
				# when we exit compileExpression, curToken = ']'

				self.w(self.line)			# ']'
				self.w('</term>\n')			# close term section


				# add value of expression to the stored address
				self.vm.writeArithmetic('add')
				self.vm.writePop('pointer', 1)
				self.vm.writePush('that', 0)
				self.vm.writePop('temp',1)

				# reinstate state of 'that' pointer 
				self.vm.writePush('temp',0)
				self.vm.writePop('pointer',1)

				self.vm.writePush('temp',1)

				self.nextToken()

				return

			# case when: subroutine(expressionList) or 
			# class/varName.subroutine(expressionList)
			elif lookAhead in ['(', '.']:

				self.compileSubroutineCall()


			# case when identifier is just varName or keywordConstant
			# e.g. if(x) <-- x is just a varName
			else: 
				# identifier
				self.w('<identifier> used ' + self.sTable.returnAttr(self.curToken) + ' </identifier>\n')
				self.w('</term>\n')			# close term section

				# we just push variable to stack
				kind  = CompilationEngine.vmKind[self.sTable.kindOf(self.curToken)]
				index = self.sTable.indexOf(self.curToken)
				self.vm.writePush(kind, index)

				self.nextToken()
				return

		else: 
			return

		# for now, curToken is ';' or ')' or ',' when we exit out of compileTerm


	def compileExpressionList(self):
		'''
		Compiles a ( possibly empty) comma-separated list of expressions.
		For the VM file, count the number of arguments.
		'''
		self.w('<expressionList>\n')
		# when we enter compileExpressionList, curToken is '('

		numArgs = 0 

		while self.curToken:

			if self.curToken == ')':
				self.w('</expressionList>\n')
				return numArgs

			elif self.curToken == ',':
				self.w(self.line)			# ','
				self.nextToken()
				self.compileExpression()
				numArgs += 1

			else: 
				self.compileExpression()
				numArgs += 1


