from enum import Enum
from typing import Callable,List,Tuple,Optional

#had to import re
import re

class ScannerException(Exception):
    
    # this time, the scanner exception takes a line number
    def __init__(self, lineno:int) -> None:
        message = "Scanner error on line: " + str(lineno)
        super().__init__(message)
        

class Token(Enum):
    ID     = "ID"
    NUM    = "NUM"
    IGNORE = "IGNORE"
    PLUS = "PLUS"
    MULT = "MULT"
    SEMI = "SEMI"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    ASSIGN = "ASSIGN"
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    INT = "INT"
    FLOAT = "FLOAT"
    SUB = "SUB"
    DIV = "DIV"
    LESS = "LESS"
    EQUAL = "EQUAL"
    END = "END"

class Lexeme:
    def __init__(self, token:Token, value:str) -> None:
        self.token = token
        self.value = value

    def __str__(self) -> str:
        return "(" + str(self.token) + "," + "\"" + self.value + "\"" + ")"    


class Scanner:
    def __init__(self, tokens: List[Tuple[Token,str,Callable[[Lexeme],Lexeme]]]) -> None:
        self.tokens = tokens
        self.lineno = 1

    def input_string(self, input_string:str) -> None:
        self.istring = input_string

    # Get the scanner line number, needed for the parser exception
    def get_lineno(self)->int:
        return self.lineno
    def token(self) -> Optional[Lexeme]:
        # Loop until we find a token we can
        # return (or until the string is empty)
        while True:
            if len(self.istring) == 0:
                #added END token to make it easier for parser
                return Lexeme("END", "")

            # For each substring

            matches = []

            # Check each token
            for t in tokens:
                # Create a tuple for each token:
                # * first element is the token type
                # * second is the possible match
                # * third is the token action
                matches.append((t[0],
                                re.match(t[1],self.istring),
                                t[2]))

            # Check if there is any token that returned a match
            # If so break out of the substring loop
            matches = [m for m in matches if m[1] is not None]
                            
            if len(matches) == 0:
                #add lineno to the scanner error
                raise ScannerException(self.lineno)     
            
            longest = matches[0]
            topLength = len(matches[0][1].group())
            for match in matches:
                if len(match[1].group()) > topLength:
                    longest = match
                    topLength = len(match[1].group())


            # apply the token action
            ret = longest[2](self, Lexeme(longest[0],longest[1][0]))

            chop = len(ret.value)
            self.istring = self.istring[chop:]

            if ret.token != Token.IGNORE:
                return ret

def idy(scanner: Scanner, l:Lexeme) -> Lexeme:
    return l


def keywords(scanner: Scanner, l: Lexeme) -> Lexeme:
    if (l.value == "if"):
        return Lexeme(Token.IF, l.value)
    if (l.value == "int"):
        return Lexeme(Token.INT, l.value)
    if (l.value == "else"):
        return Lexeme(Token.ELSE, l.value)
    if (l.value == "for"):
        return Lexeme(Token.FOR, l.value)
    if (l.value == "float"):
        return Lexeme(Token.FLOAT, l.value)
    return l


#add to cunter at every \n which is called for IGNORE tokens
def count(scanner: Scanner, l:Lexeme) -> Lexeme:
    if l.value == '\n':
        scanner.lineno += 1
    return l

# Finish providing tokens (including token actions) for the C-simple
# language
tokens = [(Token.ID,     "[a-zA-Z][a-zA-Z0-9]*",  keywords),
    (Token.NUM,    "[0-9]*\.?[0-9]+",  idy),
    (Token.IGNORE, " |\n|\t",    count),
    (Token.PLUS,   "\+",    idy),
    (Token.MULT, "\*",    idy),
    (Token.SEMI, ";",    idy),
    (Token.LPAREN, "\(",    idy),
    (Token.RPAREN, "\)",    idy),
    (Token.LBRACE, "{",    idy),
    (Token.RBRACE, "}",    idy),
    (Token.EQUAL, "==",    idy),
    (Token.ASSIGN, "=",    idy),
    (Token.SUB, "-",    idy),
    (Token.DIV, "/",    idy),
    (Token.LESS, "<",    idy),
    ]
