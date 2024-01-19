from enum import Enum


class Token(Enum):
    ID     = "ID"
    NUM    = "NUM"
    IGNORE = "IGNORE"
    HNUM = "HNUM"
    INCR = "INCR"
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
    WHILE = "WHILE"
    INT = "INT"
    FLOAT = "FLOAT"

class Lexeme:
    def __init__(self, token:Token, value:str) -> None:
        self.token = token
        self.value = value

    def __str__(self):
        return "(" + str(self.token) + "," + "\"" + self.value + "\"" + ")"    

def idy(l:Lexeme) -> Lexeme:
    return l

def keywords(l: Lexeme) -> Lexeme:
    if (l.value == "if"):
        return Lexeme(Token.IF, l.value)
    if (l.value == "int"):
        return Lexeme(Token.INT, l.value)
    if (l.value == "else"):
        return Lexeme(Token.ELSE, l.value)
    if (l.value == "while"):
        return Lexeme(Token.WHILE, l.value)
    if (l.value == "float"):
        return Lexeme(Token.FLOAT, l.value)
    return l

tokens = [
    (Token.ID,     "[a-zA-Z][a-zA-Z0-9]*",  keywords),
    (Token.HNUM,   "0x[0-9a-fA-F]+",    idy),
    (Token.NUM,    "[0-9]*\.?[0-9]+",  idy),
    (Token.IGNORE, " |\n",    idy),
    (Token.INCR,   "\+\+",    idy),
    (Token.PLUS,   "\+",    idy),
    (Token.MULT, "\*",    idy),
    (Token.SEMI, ";",    idy),
    (Token.LPAREN, "\(",    idy),
    (Token.RPAREN, "\)",    idy),
    (Token.LBRACE, "{",    idy),
    (Token.RBRACE, "}",    idy),
    (Token.ASSIGN, "=",    idy)
]
