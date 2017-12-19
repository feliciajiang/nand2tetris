import stripJackFile as s
import os


class JackTokenizer:
	'''
	Jack tokenizer 
	'''

	symbols = ['{' , '}' , '(' , ')' , '[' , ']'
				,'.', ',' , ';' , '+' , '-' , '*' 
				, '/' , '&' , '|',','
				,'<' , '>' , '=' 
				, '~']
	keywords = ['class', 'constructor', 'function', 'method', 'field'
				,'static','var' ,'int','char'
				,'boolean','void','true','false'
				,'null', 'this','let','do','if','else','while','return']
	
	# constructor
	def __init__(self,inputJackFile,AoutfileName):
		''' 
		Opens the input file/stream and gets ready to tokenize it.
		'''
		# call stripJackFile and strip all comments and blank lines (but not whitespace)
		self.strippedJackFile = os.path.abspath(inputJackFile).split('.')[0] + ".stripped"
		s.stripJackFile(os.path.abspath(inputJackFile), self.strippedJackFile)

		self.f = open(self.strippedJackFile, 'r')
		self.line = ''

		self.tokenList = []
		self.inQuote = False
		self.outfileName = AoutfileName
		self.tokenizedList = []


	def getNextToken(self):
		'''
		Function: detects, parses, and stores all tokens of a line
			to the class array tokenList
		'''

		#iterate through each character of line 
		#	1) until we hit whitespace 
		#	2) hit some symbol (eg: ; > < = ( ) { } [ ] )
		#	which indicates end of a token.

		curToken = ''

		# examine each character in line 
		for c in self.line:

			# if we hit a double quote and self.inQuote is true, 
			# we append curToken to tokenList and reset curToken to empty 
			if c == '"' and self.inQuote:
				curToken += c
				self.tokenList.append(curToken)
				self.inQuote = False
				curToken = ''

			# if we hit the first double quote of a string do not append - 
			# instead set inQuote to True 
			# corner case, empty string ""
			elif c == '"' and not self.inQuote:
				if curToken != '':
					self.tokenList.append(curToken)
				self.inQuote = True
				curToken = c

			elif self.inQuote:
				curToken += c 

			# if we hit a white space and curToken is not empty,
			# we add curToken to tokenList and reset curToken to empty
			elif c == ' ' and curToken != '' and curToken != '\n':
				self.tokenList.append(curToken)
				curToken = ''

			# if c is not a symbol, append c to the current token
			elif c != ' ' and c not in JackTokenizer.symbols:
				curToken += c 

			# if c is a symbol, we add curToken(iff curToken is not empty)
			# and the symbol to tokenList, and reset curToken to empty
			#if c in symbols:
			else:
				if c in JackTokenizer.symbols:
					if curToken != '': 
						self.tokenList.append(curToken)

					self.tokenList.append(c)
					curToken = ''


	def testGetNextToken(self):
		'''
		Test function for getNextToken()
		'''
		for l in self.f:
			self.line = l
			self.getNextToken()

		print(self.tokenList)


	def tokenType(self,token):
		'''
		In: token
		Out: KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
		Returns the type of the current token.
		'''
		if token in JackTokenizer.keywords:
			return 'KEYWORD'

		elif token in JackTokenizer.symbols:
			return 'SYMBOL'

		elif token.isdigit():
			return 'INT_CONST'

		elif token[0] == '"' and token[-1] == '"':
			return 'STRING_CONST'

		else:
			return 'IDENTIFIER'


	def keyword(self,token):
		'''
		Returns the keyword which is the current token. Should be 
		called only when tokenType() is KEYWORD.
		'''
		return '<keyword> ' + token + ' </keyword>' 

	def symbol(self,token):
		'''
		Returns the character which is the current token. 
		Should be called only when tokenType() is SYMBOL.
		'''
		# take into account XML markup exceptions 
		# (<, >, ", &)
		# &lt;, &gt;, &quot;, and &amp;
		XMLexcept = {'<':'&lt;', '>':'&gt;', '"':'&quot;', '&':'&amp;'}

		if token in XMLexcept:
			tok = XMLexcept[token]

		else:
			tok = token 

		return '<symbol> ' + tok + ' </symbol>'

	def identifier(self,token):
		'''
		Returns the identifier which is the current token. 
		Should be called only when tokenType() is IDENTIFIER.
		'''
		# check that first character is not a digit
		if token[0].isdigit():
			print('Error: identifier cannot begin with integer')
			sys.exit(0)

		else:
			return '<identifier> ' + token + ' </identifier>'

	def intVal(self,token):
		'''
		Returns the integer value of the current token. 
		Should be called only when tokenType() is INT_CONST.
		'''
		if int(token) > 32767:
			print('Error: integer value out of range')
			sys.exit(0)

		return '<integerConstant> ' + token + ' </integerConstant>'

	def stringVal(self,token):
		'''
		Returns the string value of the current token, without the double quotes. 
		Should be called only when tokenType() is STRING_CONST.
		'''
		# exclude the quotation marks at the ends 
		return '<stringConstant> '+ token[1:len(token)-1] + ' </stringConstant>'


	def getAllToken(self):
		'''
		Gets all tokens from file and puts into self.tokenList
		'''
		for l in self.f:
			self.line = l
			self.getNextToken()


	def tokenize(self):
		'''
		Out: writes xml file of tokenized version of .jack file called xxxT.xml
		Function: 
			1) calls getAllTokens to read through the entire .jack file and 
				append all tokens into a class list, called tokenList
			2) when all the correct tokens have been added to tokenList, 
				iterate through each token, identify what type it is 
				as well as any other formatting issues (using functions defined above)
			3) print the correct tags to the outfile xxxT.xml, and append each line of the 
				xxxT.xml to a class array called self.tokenizedList which is used by 
				CompilationEngine for efficiency

		'''

		self.getAllToken()
		os.remove(self.strippedJackFile)


		with open(self.outfileName,'w') as f1:

			f1.write('<tokens>\n')
			for tok in self.tokenList: 
				tokType = self.tokenType(tok)

				if tokType == 'KEYWORD':
					f1.write(self.keyword(tok)+'\n')
					self.tokenizedList.append(self.keyword(tok)+'\n')

				elif tokType == 'SYMBOL':
					f1.write(self.symbol(tok)+'\n')
					self.tokenizedList.append(self.symbol(tok)+'\n')

				elif tokType == 'IDENTIFIER':
					f1.write(self.identifier(tok)+'\n')
					self.tokenizedList.append(self.identifier(tok)+'\n')

				elif tokType == 'INT_CONST':
					f1.write(self.intVal(tok)+'\n')
					self.tokenizedList.append(self.intVal(tok)+'\n')

				else:
					f1.write(self.stringVal(tok)+'\n')
					self.tokenizedList.append(self.stringVal(tok)+'\n')


			f1.write('</tokens>')
			self.tokenizedList.append('</tokens>')
			f1.close()


	def getTokenizedList(self):
		return self.tokenizedList
