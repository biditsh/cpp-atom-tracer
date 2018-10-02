# The inject script expects on stdin (scopeInfo is what is returned by the parse script):
#   filepath variable_name scopeInfo
# And is expected to output on stdout:
#   [{line:<num>,output:<num>},...]

import json
import sys,symtable
import ast
import base64
import os
import re
from subprocess import Popen, PIPE



#Grab the arguments from stdin
filepath,variable_name,line_number = "","",""
if(len(sys.argv) == 4):
    filepath = sys.argv[1]
    variable_name = sys.argv[2]
    jsonString = base64.b64decode(sys.argv[3]).decode('ascii')
    scopeInfo = json.loads(jsonString)
else:
    raise ValueError("Incorrect number of arguments! Parse script takes exactly three arguments: filepath variable_name line_number")

start_list=[] #stores start line of the scopes
end_list=[] #stores end lines of scopes
variable_list=[] #stores corresponding variable names in each scope

# scopeInfo = json.load(open('scopeData.json'))

#make the lists from the parsed json data
function_counter = scopeInfo["function_count"]
for i in range(0,function_counter):
    variable_list.append(scopeInfo["scope"]["variable"][i])
    start_list.append(scopeInfo["scope"]["start"][i])
    end_list.append(scopeInfo["scope"]["end"][i])



temp_filepath=filepath.replace(".cpp","-temp.cpp") #create a copy for injection
os.system('cp '+filepath+' '+temp_filepath)   

def  Inject(start, end, variable_name,file_path):
    #Read the file
    fileObj = open(file_path)   #CHANGE THIS
    fileContent = fileObj.read()
    fileObj.close()
    #Split by lines
    lines = fileContent.split("\n")
    
#print statement for c++ program:
    statement = 'cout<<endl<<\"\{\\"atomic_tracer\\":true,\\"line\\":<line>,\\"output\\":\"<<\'\"\'<<'+variable_name+'<<\'\"\'<<\"\}\"<<endl;'


    #Inject print statements
    for i in range(start-1,end-1):   #we're identifying the lines that we can inject print statements to
        if(str(lines[i]).find(variable_name) > -1):
            lineNum = i+1

            if ((lines[i].find("int ") > -1 or lines[i].find("bool ") > -1 or lines[i].find("string ") > -1 or lines[i].find("char ") > -1 or lines[i].find("float ") > -1) and lines[i].find(";") > -1):
                # lines[i][lines[i].index(';')].insert(stmt)
                line_parts=lines[i].split('//')   #splits the line with // so that comments are removed
                lines[i]=line_parts[0]       #replaces line by part before comment

            # print the lines that have 'for'
            elif (lines[i].find("for") > -1):      
                stmt = statement.replace("<line>",str(lineNum))  #replace the line number in the print statemetn
                rawlines=lines[i].split(';')    #splits the for containing line by ; and adds cout in the middle of for statement
                length=len(rawlines)
                newline=rawlines[0]
                for j in range(1,length-1):
                    newline+=';'+rawlines[j]         #combines the parts of line again
                newline=newline+';'+stmt[:len(stmt)-1]+','+rawlines[length-1]
                lines[i]=newline

            # otherwise print the lines that have ';' or '{'
            elif (lines[i].find("{") > -1 and lines[i].find("if(") > -1):    
                stmt = statement.replace("<line>",str(lineNum))
                line_parts=lines[i-1].split('//')   #removing comments bys splitting
                lines[i-1]=line_parts[0]+stmt

            # otherwise print the lines that have ';' or '{'
            elif (lines[i].find(";") > -1 or lines[i].find("{") > -1):
                stmt = statement.replace("<line>",str(lineNum))
                line_parts=lines[i].split('//')    #removing comments by splitting
                lines[i]=line_parts[0]+stmt    


    #Write code to temp file
    tempFile = file_path.replace(".cpp","-temp.cpp") #create a temp file with couts injectes
    os.remove(file_path)   #delete the old file
    fileObj = open(tempFile,"w")       #write in the new file
    fileObj.write("\n".join(lines))
    fileObj.close()

    return tempFile       #returns the name of new file with couts injected


new_file=Inject(start_list[0], end_list[0],variable_list[0], temp_filepath)     #inject cout in first scope
for i in range(1,function_counter):  
    new_file=Inject(start_list[i], end_list[i],variable_list[i], new_file)   #inject cout in rest of the scopes

#Run file and get output
path_head, path_tail = os.path.split(filepath)
tempexec_path = path_head + "/temp_exec"
command = "clang++ -o " + tempexec_path +" "+ new_file
os.system(command+' 2>/dev/null')

process = Popen(['./'+tempexec_path], stdout=PIPE)
(output, err) = process.communicate()
exit_code = process.wait()
if(err):
    os.remove(new)
    raise ValueError(err.decode('utf-8'))
output = output.decode('utf-8')
#Parse output (only get the output that we injected)
lines = output.split("\n")
cleanOutput = []
for line in lines:
    try:
        out = json.loads(line)
        if('atomic_tracer' in out):
            cleanOutput.append(out)
    except:
        pass
#Delete file
os.remove(tempexec_path)
os.remove(new_file)
print(json.dumps(cleanOutput))
