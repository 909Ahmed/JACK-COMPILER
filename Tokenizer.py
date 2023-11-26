import glob, re
import os, sys


class Tokenizer ():

    def __init__(self, file):
        self.file = open(file, 'r')
        self.text = self.file.read()
        #print(self.text)
        self.tokens = []
        self.keywords = ['class', 'constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
        self.symbols = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
        self.xml = {'<':'&lt;', '>':'&gt;','&':'&amp;','"':'&quot;'}
        self.counter = 0
        self.getEle()
        self.current_token = 'class'
        self.all_tokens = self.tokens
        
        
    def getEle(self):
        self.text = re.sub(re.compile('/\*.*?\*/',re.DOTALL ),"",self.text)
        self.text = re.sub(re.compile('//.*?\n'),"",self.text)
        pattern = '|'.join(self.keywords)+'|"[^"]*"|\w+'+'|'+'|\\'.join(self.symbols)
        self.tokens = re.findall(pattern, self.text)

    def hasMoreLines(self):
        
        return self.counter < len(self.tokens)

    def advance(self):
    
        if self.hasMoreLines == False:
            return 
        
        self.counter += 1
        self.current_token = self.tokens[self.counter]
        

    def return_typetoken(self):
        token = self.current_token
        if token in self.keywords:
            return 'keyword'
        elif token in self.symbols:
            return 'symbol'
        elif token.isdigit():
            return 'integerconstant'
        elif token[0] == '"' and token[-1] == '"':
            return 'stringconstant'
        elif token[0].isdigit() == False:
            return 'identifier'
        else:
            return 'INVALID_TOKEN'
    def current_token(self):

        return self.tokens[self.counter  + 1];


    def keyWord(self):
    
        return self.current_token

        
    def symbol(self):


        if self.current_token in self.xml:
            return self.xml[self.current_token]
        return self.current_token
        
    def identifier(self):

        return self.current_token
        
    def intVal(self):

        return int(self.current_token)
        
    def stringVal (self):

        return self.current_token[1:-1]
        
