
from Tokenizer import Tokenizer

class symbolTable :
    Table_classvarDec = []
    Table_subroutinevarDec = []
    def __init__(self,file):
        self.tokenizer = Tokenizer(file)
        self.static_counter=0
        self.field_counter=0
        self.argument_counter=0
        self.local_counter=0
        self.while_counter = 0
        self.if_counter=0
    
    def compile_classvarDec(self):
        row = []
        if (self.tokenizer.current_token == "static"):
            row.append(self.tokenizer.current_token)
            self.tokenizer.advance()
            row.append(self.tokenizer.current_token)
            self.tokenizer.advance()
            self.compile_varName(row,True,"static")
        if (self.tokenizer.current_token == "field"):
            row.append(self.tokenizer.current_token)
            self.tokenizer.advance()
            row.append(self.tokenizer.current_token)
            self.tokenizer.advance()
            self.compile_varName(row,True,"field")
    
    def compile_arguments(self):
        row=[]
        row.append("argument")
        row.append(self.tokenizer.current_token)
        self.tokenizer.advance()
        row.append(self.tokenizer.current_token)
        row.append(self.argument_counter)
        self.tokenizer.advance()
        self.argument_counter+=1
        self.Table_subroutinevarDec.append(row)
        if(self.tokenizer.current_token == ','):
            self.tokenizer.advance()
            self.compile_arguments()

    def compile_subroutine(self):
        if (self.tokenizer.current_token == "var"):
            row = []
            row.append("local")
            self.tokenizer.advance()
            row.append(self.tokenizer.current_token) 
            self.tokenizer.advance()
            self.compile_varName(row,False,"local")

    def compile_varName(self,Table,flag,type):
        Table.append(self.tokenizer.current_token)
        if(type=="static"):
            Table.append(self.static_counter)
            self.static_counter+=1
        elif (type == "field"):
            Table.append(self.field_counter)
            self.field_counter += 1
        elif(type=="local"):
            Table.append(self.local_counter)
            self.local_counter+=1
        if(flag):
            self.Table_classvarDec.append(Table)
        else:
            self.Table_subroutinevarDec.append(Table)

        self.tokenizer.advance()
        if (self.tokenizer.current_token == ','):
            self.tokenizer.advance()
            new_table = Table[0:2]
            self.compile_varName(new_table,flag,new_table[0])
        if (self.tokenizer.current_token == ';'):
            self.tokenizer.advance()
            if(flag):
                self.compile_classvarDec()
            else:
                self.compile_subroutine()

    def return_row(self, name):
        for row in self.Table_subroutinevarDec :
            if (row[2] == name):
                return row
        for row in self.Table_classvarDec :
            if (row[2] == name):
                return row

    def clear_subroutineTable(self):
        self.Table_subroutinevarDec = []
        self.local_counter=0
        self.argument_counter=0
