from symbolTable import symbolTable
from VMWriter import VMWriter
import sys, os


class CompileEngine:
    Operators = ['+', '-', '*', '/', '|', '<', '&', '>']
    methods=["constructor","function","method"]

    def __init__(self,file):
        self.symbolTable = symbolTable(file)
        self.output_file = self.get_file(file)
        self.vmwriter = VMWriter(self.output_file)
        self.left_arrflag = False
        self.right_arrflag = False
        self.eq_flag = False
        self.letflag=False
        self.class_name=''
        self.argscounter=0
        self.left_counter=0
        self.right_counter=0
        self.name_methods=[]
        self.findmethods()
    
    
    def get_file(self,file):
        out_putfile = file.replace('.jack', '.vm')
        output_file = open(out_putfile, 'w')
        return output_file
    
    def findmethods(self):
        for i in range(len(self.symbolTable.tokenizer.all_tokens)):
            if self.symbolTable.tokenizer.all_tokens[i] == "method":
                self.name_methods.append(self.symbolTable.tokenizer.all_tokens[i+2])
    
    def compileClass(self):
        self.symbolTable.tokenizer.advance()
        self.class_name+=self.symbolTable.tokenizer.current_token
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.compile_classvarDec()

        while(self.symbolTable.tokenizer.current_token in self.methods):
            if(self.symbolTable.tokenizer.current_token == "constructor"):
                self.compile_constructor()
            elif(self.symbolTable.tokenizer.current_token == "function"):
                self.compile_function()
            elif (self.symbolTable.tokenizer.current_token == "method"):
                self.compile_method()

    def compile_constructor(self):
        self.symbolTable.clear_subroutineTable()
        self.symbolTable.tokenizer.advance()
        constructur_name=self.symbolTable.tokenizer.current_token
        self.symbolTable.tokenizer.advance()  
        self.symbolTable.tokenizer.advance()  
        self.symbolTable.tokenizer.advance()
        if (self.symbolTable.tokenizer.current_token != ')'):
            self.symbolTable.compile_arguments()
        self.symbolTable.tokenizer.advance()  
        self.symbolTable.tokenizer.advance()  
        self.symbolTable.compile_subroutine()
        self.vmwriter.write_function(constructur_name + '.new' , str(self.symbolTable.local_counter))
        self.output_file.write("push constant " + str(self.symbolTable.field_counter) + '\n')
        self.output_file.write("call Memory.alloc 1" + '\n')
        self.output_file.write("pop pointer 0" + '\n') 
        self.compile_statements()
        self.symbolTable.tokenizer.advance()

    def compile_function(self):
        self.symbolTable.clear_subroutineTable()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        name=self.symbolTable.tokenizer.current_token
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        if (self.symbolTable.tokenizer.current_token != ')'):
            self.symbolTable.compile_arguments()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.compile_subroutine()
        self.vmwriter.write_function(self.class_name+'.'+name,self.symbolTable.local_counter)
        self.compile_statements()
        self.symbolTable.tokenizer.advance()

    def compile_method(self):
        self.symbolTable.clear_subroutineTable()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        name=self.symbolTable.tokenizer.current_token
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.Table_subroutinevarDec.append(["argument",self.class_name,"this",self.symbolTable.argument_counter])
        self.symbolTable.argument_counter+=1
        if (self.symbolTable.tokenizer.current_token != ')'):
            self.symbolTable.compile_arguments()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        self.symbolTable.compile_subroutine()
        self.vmwriter.write_function(self.class_name + '.' + name, self.symbolTable.local_counter)
        self.vmwriter.write_push("argument",0)
        self.vmwriter.write_pop("pointer",0)
        self.compile_statements()
        self.symbolTable.tokenizer.advance()

    def compile_excpression(self):
        self.compile_term()
        while(self.symbolTable.tokenizer.current_token in self.Operators or self.symbolTable.tokenizer.current_token == '='):
            
            operator=self.symbolTable.tokenizer.current_token
            self.symbolTable.tokenizer.advance()
            self.compile_term()
            self.vmwriter.writeArthimetcs(operator)

    def compile_term(self):

        if(self.symbolTable.tokenizer.return_typetoken() == "integerconstant"):
            self.vmwriter.write_push("constant", self.symbolTable.tokenizer.current_token)
            self.symbolTable.tokenizer.advance()
        elif(self.symbolTable.tokenizer.return_typetoken() == "stringconstant"):
            self.handle_str()
            self.symbolTable.tokenizer.advance()
        elif (self.symbolTable.tokenizer.return_typetoken() == "keyword"):
            if(self.symbolTable.tokenizer.current_token == "null" or self.symbolTable.tokenizer.current_token == "false"):
                self.vmwriter.write_push("constant",0)
                self.symbolTable.tokenizer.advance()
            elif(self.symbolTable.tokenizer.current_token == "this"):
                self.vmwriter.write_push("pointer",0)
                self.symbolTable.tokenizer.advance()
            elif(self.symbolTable.tokenizer.current_token == "true"):
                self.vmwriter.write_push("constant",0)
                self.vmwriter.writeArthimetcs('not')
                self.symbolTable.tokenizer.advance()
        elif(self.symbolTable.tokenizer.current_token == '('):
            self.symbolTable.tokenizer.advance()
            self.compile_excpression()
            self.symbolTable.tokenizer.advance()
        elif (self.symbolTable.tokenizer.return_typetoken() == "identifier"):
            var_name=self.symbolTable.tokenizer.current_token
            if(self.symbolTable.tokenizer.all_tokens[self.symbolTable.tokenizer.counter+1] == '['):
                if(self.eq_flag):
                    self.right_arrflag = True
                else:
                    self.left_arrflag = True
                if(self.right_arrflag):
                    self.right_counter+=1
                else:
                    self.left_counter+=1
                self.compile_arr(var_name)
                if(not self.letflag):
                    self.left_arrflag = False
            elif(self.symbolTable.tokenizer.all_tokens[self.symbolTable.tokenizer.counter+1] == '.'):
                self.handle_point(var_name)
            elif (self.symbolTable.tokenizer.all_tokens[self.symbolTable.tokenizer.counter + 1] == '('):
                self.compile_subroutinecall(var_name)
            else:
                row = self.symbolTable.return_row(var_name)
                self.vmwriter.write_push(row[0],row[3])
                self.symbolTable.tokenizer.advance()

        elif(self.symbolTable.tokenizer.current_token == '~' or self.symbolTable.tokenizer.current_token == '-'):
            operator=self.symbolTable.tokenizer.current_token
            self.symbolTable.tokenizer.advance()
            self.compile_term()
            if (operator == '~'):
                self.vmwriter.writeArthimetcs("not")
            else:
                self.vmwriter.writeArthimetcs("neg")   


    def compile_subroutinecall(self,name):
        argscounter = 0
        if (name in self.name_methods):
            self.vmwriter.write_push("pointer",0)
            argscounter+=1
        self.symbolTable.tokenizer.advance()  
        self.symbolTable.tokenizer.advance()  
        argscounter=self.handle_parameters(argscounter) 
        self.vmwriter.write_call(self.class_name+'.'+name, argscounter)
        self.symbolTable.tokenizer.advance()  

    def compile_statements(self):
        if (self.symbolTable.tokenizer.current_token == "let"):
            self.compile_let()
            self.compile_statements()
        if (self.symbolTable.tokenizer.current_token == "do"):
            self.compile_do()
            self.compile_statements()
        if (self.symbolTable.tokenizer.current_token == "return"):
            self.compile_return()
            self.compile_statements()
        if (self.symbolTable.tokenizer.current_token == "if"):
            self.compile_if()
            self.compile_statements()
        if (self.symbolTable.tokenizer.current_token == "while"):
            self.compile_while()
            self.compile_statements()

    def compile_let(self):
        self.letflag=True
        self.symbolTable.tokenizer.advance() 
        varname = self.symbolTable.tokenizer.current_token
        if (self.symbolTable.tokenizer.all_tokens[self.symbolTable.tokenizer.counter+1]== '['):
            self.left_arrflag=True
            self.left_counter+=1
            self.compile_arr(varname)
        else:
            self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance() 
        self.eq_flag = True
        self.compile_excpression()
        if (self.left_counter == 1 and self.left_arrflag):
            self.vmwriter.write_pop("temp", 0)
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("temp", 0)
            self.vmwriter.write_pop("that", 0)
            self.left_counter-=1
        if (self.left_arrflag == False):
            row = self.symbolTable.return_row(varname)
            self.vmwriter.write_pop(row[0],row[3])
        self.left_arrflag = False

        self.symbolTable.tokenizer.advance()  
        self.eq_flag = False
        self.letflag=False

    def compile_do(self):
        self.symbolTable.tokenizer.advance() 
        name = self.symbolTable.tokenizer.current_token
        if (self.symbolTable.tokenizer.all_tokens[self.symbolTable.tokenizer.counter+1] == '('):
            self.compile_subroutinecall(name)
        elif (self.symbolTable.tokenizer.all_tokens[self.symbolTable.tokenizer.counter + 1] == '.'):
            self.handle_point(name)
        self.symbolTable.tokenizer.advance()
        self.vmwriter.write_pop("temp",0)

    def compile_return(self):
        self.symbolTable.tokenizer.advance()
        if(self.symbolTable.tokenizer.current_token != ';'):
            self.compile_excpression()
            self.symbolTable.tokenizer.advance()
        else:
            self.symbolTable.tokenizer.advance()
            self.vmwriter.write_push("constant",0)
        self.vmwriter.write_return()

    def compile_if(self):
        counter=self.symbolTable.if_counter
        self.symbolTable.if_counter+=1
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        self.compile_excpression()
        self.symbolTable.tokenizer.advance()
        self.vmwriter.write_ifgoto("IFTRUE_"+str(counter))
        self.vmwriter.write_goto("IFFALSE_"+str(counter))
        self.vmwriter.write_Label("IFTRUE_"+str(counter))
        self.symbolTable.tokenizer.advance()
        self.compile_statements()
        self.symbolTable.tokenizer.advance()
        self.vmwriter.write_goto("IFEND_" + str(counter))
        if (self.symbolTable.tokenizer.current_token != "else"):
            self.vmwriter.write_Label("IFFALSE_"+ str(counter))
            self.vmwriter.write_Label("IFEND_" + str(counter))
        elif(self.symbolTable.tokenizer.current_token == "else"):
            self.vmwriter.write_Label("IFFALSE_" + str(counter))
            self.symbolTable.tokenizer.advance()
            self.symbolTable.tokenizer.advance()
            self.compile_statements()
            self.vmwriter.write_Label("IFEND_" + str(counter))
            self.symbolTable.tokenizer.advance()

    def compile_while(self):
        counter = self.symbolTable.while_counter
        self.symbolTable.while_counter+=1
        self.vmwriter.write_Label("WHILE_STATEMENT_"+str(counter))
        self.symbolTable.tokenizer.advance()
        self.symbolTable.tokenizer.advance()
        self.compile_excpression()
        self.vmwriter.writeArthimetcs("not")
        self.symbolTable.tokenizer.advance()
        self.vmwriter.write_ifgoto("WHILE_END_" + str(counter))
        self.symbolTable.tokenizer.advance()
        self.compile_statements()
        self.vmwriter.write_goto("WHILE_STATEMENT_"+str(counter))
        self.vmwriter.write_Label("WHILE_END_"+str(counter))
        self.symbolTable.tokenizer.advance()


    def compile_arr(self,arr_name):
        row = self.symbolTable.return_row(arr_name)
        self.vmwriter.write_push(row[0], row[3])
        self.symbolTable.tokenizer.advance() #[
        self.symbolTable.tokenizer.advance()
        self.compile_excpression()
        self.vmwriter.writeArthimetcs('+')
        if (self.left_counter > 1 and self.left_arrflag and self.letflag):
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
            self.left_counter -= 1
        elif (self.left_counter > 0 and self.left_arrflag and not self.letflag):
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
            self.left_counter -= 1
        elif(self.right_counter > 0 and self.right_arrflag):
            self.vmwriter.write_pop("pointer", 1)
            self.vmwriter.write_push("that", 0)
            self.right_counter -= 1
        self.arr_flag = False

        self.compile_term()

        self.symbolTable.tokenizer.advance()
        while (self.symbolTable.tokenizer.current_token in self.Operators):
            operator = self.symbolTable.tokenizer.current_token
            self.symbolTable.tokenizer.advance()
            self.compile_term()
            self.vmwriter.writeArthimetcs(operator)


    def handle_parameters(self,argscounter): 
        if (self.symbolTable.tokenizer.current_token != ')'):
            argscounter += 1
            self.compile_term()
            while (self.symbolTable.tokenizer.current_token in self.Operators):
                operator = self.symbolTable.tokenizer.current_token
                self.symbolTable.tokenizer.advance()
                self.compile_term()
                self.vmwriter.writeArthimetcs(operator)
            if (self.symbolTable.tokenizer.current_token == ','):
                self.symbolTable.tokenizer.advance()
                argscounter=self.handle_parameters(argscounter)
        return argscounter

    def handle_point(self,name):
        row = self.symbolTable.return_row(name)
        if (row != None): 
            self.vmwriter.write_push(row[0], row[3])
            self.symbolTable.tokenizer.advance()  
            self.symbolTable.tokenizer.advance()  
            func_cal = row[1] + "." + self.symbolTable.tokenizer.current_token
        else:  
            self.symbolTable.tokenizer.advance()  
            self.symbolTable.tokenizer.advance()  
            func_cal = name + "." + self.symbolTable.tokenizer.current_token
        self.symbolTable.tokenizer.advance()  
        self.symbolTable.tokenizer.advance()  
        self.argscounter = 0
        argscounter=0
        argscounter=self.handle_parameters(0) 
        if (row != None):
            self.vmwriter.write_call(func_cal, argscounter + 1)
        else:
            self.vmwriter.write_call(func_cal, argscounter)
        self.symbolTable.tokenizer.advance() 

    def handle_str(self):
        str = self.symbolTable.tokenizer.current_token[1:-1]
        self.vmwriter.write_push("constant", len(str))
        self.vmwriter.write_call("String.new", 1)
        for i in str:
            self.vmwriter.write_push("constant", ord(i))
            self.vmwriter.write_call("String.appendChar", 2)
