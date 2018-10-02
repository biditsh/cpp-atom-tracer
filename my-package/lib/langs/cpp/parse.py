import json
import sys,symtable
import ast
import ntpath
import os
import re
import subprocess

#Some helper functions
main_start= 0
main_end =0

#Grab the arguments from stdin
filepath,variable_name,line_number = "","",""
if(len(sys.argv) == 4):
    filepath = sys.argv[1]
    variable_name = sys.argv[2]
    line_number = int(sys.argv[3])

class func: # class to contain a function's info as found in the AST of the C++ code
    name = ""
    args = []
    start_line = 0 # the start of the scope
    end_line = 0 # the end of the scope
    def description(self):
        desc_str = "%s is a function starting at %s and ending at %s." % (self.name, self.kind, self.start_line, self.end_line)
        return desc_str


#regular expressions used to parse the AST components
#regular expression to find function declarations
regex_scopes = r"FunctionDecl .* \<.*:([^,]*):[0-9]*, \w+:([^)]*):[0-9]*\>.* (.*) '(.*) \((.*)\)'" 
#regular expression to find declaration of variable
regex_vars = r"DeclStmt .* \<line:([^,]*):[0-9]*, col:[0-9]*\>\n.*VarDecl.* ("+variable_name+") '(.*)'"
#regular expression to find variable declaration in function
regex_function = r"\| `-DeclRefExpr.*lvalue Function.*'(.*)' '.*"
#regular expression to find parameter of a function
regex_functionvar=r"\| \|-ParmVarDecl.* (.*) '(.*)'"
regex_functionarg=r"\|* *-DeclRefExpr.*lvalue .*Var.*'(.*)' '.*'"



def Parse():
	
	#split file path and add it to to the path of the ast file
	path_head, path_tail = os.path.split(filepath)
	dump_path = str(path_head) + "/dump.ast"

	#create command to compile using clang and direct to a file to parse
	command = 'clang++ -cc1 -ast-dump ' + filepath + ' >' + dump_path

	#run the clang command
	os.system(command+' 2>/dev/null')

	
	fileObj=open(dump_path)
	fileContent = fileObj.read() #read-in dump.txt
	fileObj.close()
	os.remove(dump_path)

	#split ast file by new line
	lines=fileContent.split("\n")
	line_no=0 #stores number of line being analysing
	start_of_call=0

	FunctionList = [] #stores the name of the functions
	function_count=0 #stores the number of the function
	scope_start_list=[] #stores start of the scope of variable
	scope_end_list=[] #stores end of the scope of variable
	scope_variable_names=[] #stores name of variable in each scope

	for line in lines: #parse line by line
		if 'FunctionDecl' in line: #check if line is start of function declaration
			line_p = re.compile(regex_scopes) #check for regex in line
			FunctionDecl = func()
			FunctionDecl.start_line = int(line_p.search(line).group(1)) #store beginning of the scope
			FunctionDecl.end_line = int(line_p.search(line).group(2)) #store end of the scope
			FunctionDecl.name = line_p.search(line).group(3) #store function name
			FunctionDecl.kind = line_p.search(line).group(4)

			local_line_no0=line_no
			while 'ParmVarDecl' in lines[local_line_no0+1]:
				functionvar_p=re.compile(regex_functionvar)
				FunctionDecl.args.append(functionvar_p.search(lines[local_line_no0+1]).group(1))
				local_line_no0+=1

			FunctionList.append(FunctionDecl)

		if 'CallExpr' in line: #check for function call in line
			local_line_no=line_no
			func_p=re.compile(regex_function, re.MULTILINE) #check for regex in line
			function_name = func_p.search(lines[local_line_no+2]).group(1) #store function name being called


			decl_counter=0
			position=line.count('|')+1
			cursor_position=position
			while (cursor_position==position or (cursor_position+lines[local_line_no].count('`-'))==position):
				if 'DeclRefExpr' in lines[local_line_no]:
					decl_counter+=1  #decl_counter-1 is the nth argument that variabe was passed by reference as
				if 'DeclRefExpr' in lines[local_line_no] and variable_name in lines[local_line_no] and 'ImplicitCastExpr' not in lines[local_line_no-1]:
					functionarg_p=re.compile(regex_functionarg, re.MULTILINE)
					function_arg=functionarg_p.search(lines[local_line_no]).group(1)
					if function_arg==variable_name:   #checks if variable_name was the one passed by reference
						#filling up the lists
						argument_position=decl_counter-1 #nth argument has given variable
						for j in range(0,len(FunctionList)):
							if FunctionList[j].name==function_name:
								scope_start_list.append(FunctionList[j].start_line)
								scope_end_list.append(FunctionList[j].end_line)
								scope_variable_names.append(FunctionList[j].args[argument_position-1])
								function_count+=1   #incrementing the function count


				local_line_no+=1
				cursor_position=lines[local_line_no].count('|')

		line_no+=1

	#appending main() information to the scope information
	for j in range(0,len(FunctionList)):
		if FunctionList[j].name=="main":
			scope_start_list.append(FunctionList[j].start_line)
			scope_end_list.append(FunctionList[j].end_line)
			scope_variable_names.append(variable_name)
	function_count+=1  #incrementing the function count for main

	var_p = re.compile(regex_vars, re.MULTILINE)
	var_line = var_p.search(fileContent).group(1)

	#construct the json string to pass to the inject script as input
	scopeData = {'scope':{
                    'start':scope_start_list,
                    'end':scope_end_list,
                    'variable':scope_variable_names
                    },
                'decl':{'line':var_line},
                'function_count':function_count
                }
	print(json.dumps(scopeData))

Parse()
