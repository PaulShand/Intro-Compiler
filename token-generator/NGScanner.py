import re
from functools import reduce
from time import time
import argparse
import pdb
import sys
sys.path.append("../part2/")
from tokens import tokens,Token,Lexeme
from typing import Callable,List,Tuple,Optional

# No line number this time
class ScannerException(Exception):
    pass

class NGScanner:
    def __init__(self, tokens: List[Tuple[Token,str,Callable[[Lexeme],Lexeme]]]) -> None:
        self.tokens = tokens

    def input_string(self, input_string:str) -> None:
        self.istring = input_string
        
    def token(self) -> Optional[Lexeme]:
        SINGLE_RE = ""
        for t in tokens:
            SINGLE_RE += "(?P<" + t[0].value + ">" + t[1] + ")|"
        SINGLE_RE = SINGLE_RE[:-1]

        while True:
            if len(self.istring) == 0:
                return None
            
            matches = re.match(SINGLE_RE,self.istring).groupdict()
            if matches:
                for m in matches.items():
                    if m[1] != None:
                        tokenized = [m[0],m[1]]
                        break
            else:
                raise ScannerException() 
            
            for tok in tokens:
                if tokenized[0] == tok[0].value:
                    ret = tok[2](Lexeme(tok[0],tokenized[1]))
                    break

            chop = len(ret.value)
            self.istring = self.istring[chop:]

            if ret.token != Token.IGNORE:
                return ret

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', type=str)
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    
    f = open(args.file_name)    
    f_contents = f.read()
    f.close()

    verbose = args.verbose

    s = NGScanner(tokens)
    s.input_string(f_contents)

    start = time()
    while True:
        t = s.token()
        if t is None:
            break
        if (verbose):
            print(t)
    end = time()
    print("time to parse (seconds): ",str(end-start))    
