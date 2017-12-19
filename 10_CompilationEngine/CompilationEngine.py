import stripJackFile as s
import JackTokenizer as jt
import os



class CompilationEngine:

	ops = [ '+' , '*' , '/' , '-'
		, '&' , '|',',' ,'<' , '>' , '=' 
		, '&lt;', '&gt;', '&quot;', '&amp;']

	unaryOps = ['~','-']

	def __init__(self,jackTokenizerOutput,outfileName):
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
		else:
			self.curToken = self.line.split()[1] # the second item in a line is the token
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
		
		self.nextToken()
		self.w(self.line)		# <identifier> Main </identifier> (or some other identifier)
		
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

		self.nextToken()			# this should be a type 
		self.w(self.line)			# <keyword> void, int, char, boolean, classname  </keyword>

		while self.curToken != ';': 
			self.nextToken()
			self.w(self.line)

		# when we exit this while loop, self.curToken = ';'

		self.w('</classVarDec>\n')	# end classVarDec section 
		self.nextToken()			# advance to next token before returning
		
		return 


	def compileSubroutine(self):
		'''
		Compiles a complete method, function, or constructor.
		'''
		# start subroutineDeclaration section
		self.w('<subroutineDec>\n')

		# curToken when we enter compileClassVar is constructor, function, or method
		self.w(self.line)		# <keyword> constructor, function, or method </keyword>

		self.nextToken()		# type 
		self.w(self.line)		# void, int, char, boolean, or className 

		self.nextToken()		# subroutineName
		self.w(self.line)		

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

		while self.curToken:

			if self.curToken == 'var':
				self.compileVarDec()

			elif self.curToken in ['let', 'if', 'else', 'while', 'do', 'return']:
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
				self.w(self.line)
				self.nextToken()


	def compileVarDec(self):
		'''
		Compiles a var declaration.
		'''
		# curToken is 'var' when we enter this function 
		# start varDeclaration section
		self.w('<varDec>\n')

		self.w(self.line)	# 'var'

		self.nextToken()	# type: 'void', int', 'char', 'boolean' or className
		self.w(self.line)

		self.nextToken()

		while self.curToken:
			if self.curToken == ';':
				self.w(self.line)
				# end varDeclaration section 
				self.w('</varDec>\n')
				self.nextToken()
				return

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

		self.nextToken()
		self.w(self.line)			# identifier (e.g. 'draw')

		# account for cases of subroutine call like 'Memory.dealloc'

		self.nextToken()
		if self.curToken == '.':
			self.w(self.line)		# '.'
			self.nextToken()	
			self.w(self.line)		# subroutineName
			self.nextToken()


		self.w(self.line)			# '('

		self.nextToken()
		self.compileExpressionList()

		# when we exit compileExpressionList, curToken = ')'
		self.w(self.line)			# ')'

		self.nextToken()
		self.w(self.line)			# ';'

		self.w('</doStatement>\n')
		self.nextToken()


	def compileLet(self):
		'''
		Compiles a let statement.
		'''
		# curToken = 'let' when we enter this function
		self.w('<letStatement>\n')
		self.w(self.line)			# 'let'
		
		self.nextToken()
		self.w(self.line)			# varName

		self.nextToken()

		# if we have brackets, like a[i], then expression in index
		if self.curToken == '[':
			self.w(self.line)		# '['

			self.nextToken()
			self.compileExpression()

			# when we exit out of compileExpression, curToken = ']'
			self.w(self.line)		# ']'
			self.nextToken()

		# next line is '='
		self.w(self.line)			# '='

		self.nextToken()
		self.compileExpression()

		self.w(self.line)			# ';'


		self.w('</letStatement>\n')
		self.nextToken()


	def compileWhile(self):
		'''
		Compiles a while statement.
		'''
		# curToken = 'while' when we enter this function

		self.w('<whileStatement>\n')
		self.w(self.line)			# 'while'

		self.nextToken()
		self.w(self.line)			# '('

		# no expression in this version yet 
		self.nextToken()
		self.compileExpression()

		self.w(self.line)			# ')' 		

		self.nextToken()
		self.w(self.line)			# '{' 

		self.nextToken()
		self.compileStatements()
		# when we exit out of compileStatements, curToken = '}'

		self.w(self.line)			# '}'
		self.w('</whileStatement>\n')
		self.nextToken()



	def compileReturn(self):
		'''
		Compiles a return statement.
		''' 
		# curToken = 'return' when we enter this function
		self.w('<returnStatement>\n')

		self.w(self.line)				# 'return'

		self.nextToken()
		if self.curToken == ';':
			self.w(self.line)			# ';' if 'return;'

		else:
			self.compileExpression()	# expression stuff
			self.w(self.line)			# ';'


		self.w('</returnStatement>\n')
		self.nextToken()


	def compileIf(self):
		'''
		Compiles an if statement, possibly with a trailing else clause.
		'''
		# curToken = 'if' when we enter this function

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

		self.nextToken()
		self.compileStatements()
		# when we exit out of compileStatements, curToken = '}'

		self.w(self.line)			# '}'

		self.nextToken()

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

			elif self.curToken in CompilationEngine.unaryOps and lookBack == '(':
				self.compileTerm()
				# curToken = ??? when we exit compileTerm for something like 
				# let i = i + (-x);


			elif self.curToken in CompilationEngine.ops:
				self.w(self.line)		# some operator like +, -, *, >, <
				self.nextToken()

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

		if self.curTokenType in ['<integerConstant>', '<stringConstant>']:
			self.w(self.line)				# int or str constant
			self.w('</term>\n')
			self.nextToken()
			return

		elif self.curToken in ['true','false','null','this']:
			self.w(self.line)				# keyword true false or null
			self.w('</term>\n')
			self.nextToken()
			return	

		elif self.curToken in ['-','~']:
			self.w(self.line)				# '-' or '~'

			self.nextToken()
			self.compileTerm()

			self.w('</term>\n')
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

			# case when its varName[expression]
			if lookAhead == '[':
				self.w(self.line)			# identifier here
				
				self.nextToken()
				self.w(self.line)			# '['

				self.nextToken()
				self.compileExpression()
				# when we exit compileExpression, curToken = ']'

				self.w(self.line)			# ']'
				self.w('</term>\n')			# close term section
				self.nextToken()
				return

			# case when: subroutine(expressionList) or 
			# class/varName.subroutine(expressionList)
			elif lookAhead in ['(', '.']:

				self.w(self.line)			# identifier (subroutine or class/varname)

				# account for cases of subroutine call like 'Memory.dealloc'

				self.nextToken()
				if self.curToken == '.':
					self.w(self.line)		# '.'
					self.nextToken()	
					self.w(self.line)		# subroutineName
					self.nextToken()

				self.w(self.line)			# '('

				self.nextToken()
				self.compileExpressionList()

				# when we exit compileExpressionList, curToken = ')'
				self.w(self.line)			# ')'
				self.w('</term>\n')			# close term section
				self.nextToken()
				return


			# case when identifier is just varName or keywordConstant
			# e.g. if(x) <-- x is just a varName
			else: 
				self.w(self.line)			# identifier
				self.w('</term>\n')			# close term section
				self.nextToken()
				return

		else: 
			return

		# for now, curToken is ';' or ')' or ',' when we exit out of compileTerm


	def compileExpressionList(self):
		'''
		Compiles a ( possibly empty) comma-separated list of expressions.
		'''
		self.w('<expressionList>\n')
		# when we enter compileExpressionList, curToken is '('

		#self.nextToken()

		while self.curToken:

			if self.curToken == ')':
				self.w('</expressionList>\n')
				return 

			elif self.curToken == ',':
				self.w(self.line)			# ','
				self.nextToken()
				self.compileExpression()

			else: 
				self.compileExpression()


