import json
import sys,symtable
import ast
import ntpath
import os
import re

#Some helper functions
scope_start= 0
scope_end =0
#Grab the arguments from stdin
filepath,variable_name,line_number = "","",""
if(len(sys.argv) == 4):
    filepath = sys.argv[1]
    variable_name = sys.argv[2]
    line_number = int(sys.argv[3])

filepath,variable_name,line_number = "","x",14

class func: # class to contain a function's info as found in the AST of the C++ code
    name = ""
    args = []
    start_line = 0 # the start of the scope
    end_line = 0 # the end of the scope
    def description(self):
        desc_str = "%s is a function starting at %s and ending at %s." % (self.name, self.kind, self.start_line, self.end_line)
        return desc_str


#regular expressions used to parse the AST components
regex_scopes = r"FunctionDecl .* \<line:([^,]*):[0-9]*, line:([^)]*):[0-9]*\>.* (.*) '(.*) \((.*)\)'"
regex_vars = r"DeclStmt .* \<line:([^,]*):[0-9]*, col:[0-9]*\>\n.*VarDecl.* ("+variable_name+") '(.*)'"
regex_function = r"\| \| `-DeclRefExpr.*lvalue Function.*'(.*)' '.*"
regex_functionvar=r"\| \|-ParmVarDecl.* (.*) '(.*)'"




def Parse():
	os.system('clang++ -cc1 -ast-dump test.cpp > dump.txt')  #run command line with clang and dump into dump.txt... hardcoded file names for test
	fileObj=open('dump.txt')
	fileContent = fileObj.read() #read-in dump.txt
	fileObj.close()

	lines=fileContent.split("\n")
	line_no=0
	start_of_call=0

	FunctionList = []

	for line in lines:
		# print (line)
		if 'FunctionDecl' in line:
			line_p = re.compile(regex_scopes)
			FunctionDecl = func()
			FunctionDecl.start_line = int(line_p.search(line).group(1))
			FunctionDecl.end_line = int(line_p.search(line).group(2))
			FunctionDecl.name = line_p.search(line).group(3)
			FunctionDecl.kind = line_p.search(line).group(4)

			local_line_no0=line_no
			while 'ParmVarDecl' in lines[local_line_no0+1]:
				functionvar_p=re.compile(regex_functionvar)
				FunctionDecl.args.append(functionvar_p.search(lines[local_line_no0+1]).group(1))
				#print FunctionDecl.args[local_line_no0-line_no]
				local_line_no0+=1

			FunctionList.append(FunctionDecl)

			if FunctionDecl.start_line <= line_number <= FunctionDecl.end_line:
				local_line_no=line_no
				start_scope = FunctionDecl.start_line
				end_scope = FunctionDecl.end_line
				print ("variable in scope", FunctionDecl.start_line, FunctionDecl.end_line)



		if 'CallExpr' in line:
			local_line_no=line_no
			func_p=re.compile(regex_function, re.MULTILINE)
			print lines[local_line_no+2]
			function_name = func_p.search(lines[local_line_no+2]).group(1)
			#chunks=lines[local_line_no+2].split(" '")
			print ("FUNCTION", function_name)
			#print position

			decl_counter=0
			position=line.count('|')+1
			cursor_position=position
			while (cursor_position==position or (cursor_position+lines[local_line_no].count('`-'))==position):
				if 'DeclRefExpr' in lines[local_line_no]:
					decl_counter+=1
				if 'DeclRefExpr' in lines[local_line_no] and variable_name in lines[local_line_no] and 'ImplicitCastExpr' not in lines[local_line_no-1]:
					print ("fuction YAAY", local_line_no)
					print ("DeclCounter", decl_counter-1)
				local_line_no+=1
				cursor_position=lines[local_line_no].count('|')

		line_no+=1


	print ("End of function ================")

	for j in range(0,len(FunctionList)):
		print(FunctionList[j].name)

	var_p = re.compile(regex_vars, re.MULTILINE)
	var_line = var_p.search(fileContent).group(1)
	var_name = var_p.search(fileContent).group(2)
	var_type = var_p.search(fileContent).group(3)
	print (var_line, var_name, var_type)
			#print ("start: " line_numbers[0] " end: "line_numbers[1])
			#print (line_numbers)

	scopeData = {'scope':{
                    'start':start_scope,
                    'end':end_scope
                    },
                'decl':{'line':var_line}
                }
	print(json.dumps(scopeData))

Parse()
