from Tokenizer import Tokenizer
from CompileEngine import CompileEngine 
import sys, os, glob

class JackAnalyzer():

    def __init__(self, files):
    
        self.tokenizer = Tokenizer(files)
        engine = CompileEngine(files)
        engine.compileClass()


def getFiles ():

    path = sys.argv[1:]
    for filepath in path:
        files = glob.glob(os.path.join(filepath, '*.jack'))
    
    return files


def main ():

    jackfiles = getFiles()
    for file in jackfiles:
        JackAnalyzer(file)
        
main()
