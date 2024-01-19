from scanner import Lexeme,Token,Scanner
from typing import Callable,List,Tuple,Optional

# Symbol Table exception, requires a line number and ID
class SymbolTableException(Exception):
    
    def __init__(self, lineno:int, ID:str) -> None:
        message = "Symbol table error on line: " + str(lineno) + "\nUndeclared ID: " + ID
        super().__init__(message)    

#Implement all members of this class for Part 3
class SymbolTable:
    #create list of hash table
    def __init__(self) -> None:
        self.tables = [{}]
    #add whatever ID encountered to the last table (the most recent scope)
    def insert(self, ID: str, info) -> None:
        self.tables[-1][ID] = info
    #From the most recent to the largest scope check if specific ID has been declared if so return it
    def lookup(self, ID: str):
        for table in reversed(self.tables):
            if ID in table:
                return ID
        return None 
    #add table to the stack
    def push_scope(self) -> None:
        self.tables.append({})
    #delete lastest table and everything in it
    def pop_scope(self) -> None:
        self.tables.pop()

class ParserException(Exception):
    
    # Pass a line number, current lexeme, and what tokens are expected
    def __init__(self, lineno:int, lexeme:Lexeme, tokens:List[Token]) -> None:
        message = "Parser error on line: " + str(lineno) + "\nExpected one of: " + str(tokens) + "\nGot: " + str(lexeme)
        super().__init__(message)

class Parser:
    def __init__(self, scanner:Scanner, use_symbol_table:bool) -> None:
        self.scanner = scanner
        self.useSymbol = use_symbol_table
        #if -s is added create Symbol Table object to the Parser and add boolean
        if self.useSymbol:
            self.ST = SymbolTable()
        

    # Implement one function in this class for every non-terminal in
    # your grammar using the recursive descent recipe from the book
    # and the lectures for part 2

    #simple function checking if current token is expected if so move to next token else throw error
    def match(self, token):
        if self.peek.token == token:
            self.peek = self.scanner.token()
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [token])

    

    #every non terminal in the grammar is defined below checking for expected tokens and matching at every step to
    #move through the tokens
    #every definition is an if statement and if none match it raise error

    def parse(self, s:str):
        self.scanner.input_string(s)
        self.peek = self.scanner.token()
        self.p_statement_list()

    def p_statement_list(self):
        if self.peek.token == "END":
            return
        elif self.peek.token in {Token.INT, Token.FLOAT, Token.ID, Token.IF, Token.LBRACE, Token.FOR}:
            self.p_statement()
            self.p_statement_list()
        elif self.peek.token == Token.RBRACE:
            return
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.INT, Token.FLOAT, Token.ID, Token.IF, Token.LBRACE, Token.FOR, Token.RBRACE])
        
    def p_statement(self):
        if self.peek.token in{Token.INT, Token.FLOAT}:
            self.p_declaration_statement()
        elif self.peek.token == Token.ID:
            self.p_assignment_statement()
        elif self.peek.token == Token.IF:
            self.p_if_else_statement()
        elif self.peek.token == Token.LBRACE:
            self.p_block_statement()
        elif self.peek.token == Token.FOR:
            self.p_for_loop_statement()
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.INT, Token.FLOAT, Token.ID, Token.IF, Token.LBRACE, Token.FOR])

    def p_declaration_statement(self):
        if self.peek.token == Token.INT:
            self.peek = self.scanner.token()
            #when declared if use symbol is true it uses symbol table function to insert
            if self.useSymbol:
                self.ST.insert(self.peek.value, "")
            self.match(Token.ID)
            self.match(Token.SEMI)
        elif self.peek.token == Token.FLOAT:
            self.peek = self.scanner.token()
            if self.useSymbol:
                self.ST.insert(self.peek.value, "")
            self.match(Token.ID)
            self.match(Token.SEMI)
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.INT, Token.FLOAT])


    def p_assignment_statement(self):
        if self.peek.token == Token.ID:
            self.p_assignment_statement_base()
            self.match(Token.SEMI)

    def p_assignment_statement_base(self):
        #if ID used but never declred it will return None on lookup and raise error
        if self.useSymbol:
            if self.ST.lookup(self.peek.value) == None:
                raise SymbolTableException(self.scanner.get_lineno(),self.peek.value)
        self.match(Token.ID)
        self.match(Token.ASSIGN)
        self.p_expr()

    def p_if_else_statement(self):
        self.match(Token.IF)
        self.match(Token.LPAREN)
        self.p_expr()
        self.match(Token.RPAREN)
        self.p_statement()
        self.match(Token.ELSE)
        self.p_statement()

    def p_block_statement(self):
        self.match(Token.LBRACE)
        if self.useSymbol:
            self.ST.push_scope()
        self.p_statement_list()
        if self.useSymbol:
            self.ST.pop_scope()
        self.match(Token.RBRACE)

    def p_for_loop_statement(self):
        self.match(Token.FOR)
        self.match(Token.LPAREN)
        self.p_assignment_statement()
        self.p_expr()
        self.match(Token.SEMI)
        self.p_assignment_statement_base()
        self.match(Token.RPAREN)
        self.p_statement()

    def p_expr(self):
        if self.peek.token in {Token.NUM, Token.ID, Token.LPAREN}:
            self.p_comp() 
            self.p_expr2()
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.NUM, Token.ID, Token.LPAREN])

    def p_expr2(self):
        if self.peek.token == Token.EQUAL:
            self.peek = self.scanner.token()
            self.p_comp()
            self.p_expr2()
        elif self.peek.token in {Token.SEMI, Token.RPAREN}:
            return
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.EQUAL, Token.SEMI, Token.RPAREN])


    def p_comp(self):
        if self.peek.token in {Token.NUM, Token.ID, Token.LPAREN}:
            self.p_factor() 
            self.p_comp2()
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.NUM, Token.ID, Token.LPAREN])

    def p_comp2(self):
        if self.peek.token == Token.LESS:
            self.peek = self.scanner.token()
            self.p_factor()
            self.p_comp2()
        elif self.peek.token in {Token.SEMI, Token.RPAREN, Token.EQUAL}:
            return
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.LESS, Token.SEMI, Token.RPAREN, Token.EQUAL])


    def p_factor(self):
        if self.peek.token in {Token.NUM, Token.ID, Token.LPAREN}:
            self.p_term() 
            self.p_factor2()
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.NUM, Token.ID, Token.LPAREN])

    def p_factor2(self):
        if self.peek.token in {Token.PLUS, Token.SUB}:
            self.peek = self.scanner.token()
            self.p_term()
            self.p_factor2()
        elif self.peek.token in {Token.SEMI, Token.RPAREN, Token.EQUAL, Token.LESS}:
            return
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.PLUS, Token.SUB, Token.SEMI, Token.RPAREN, Token.EQUAL, Token.LESS])


    def p_term(self):
        if self.peek.token in {Token.NUM, Token.ID, Token.LPAREN}:
            self.p_unit() 
            self.p_term2() 
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.NUM, Token.ID, Token.LPAREN])


    def p_term2(self):
        if self.peek.token in {Token.MULT, Token.DIV}:
            self.peek = self.scanner.token()
            self.p_unit()
            self.p_term2()
        elif self.peek.token in {Token.SEMI, Token.RPAREN, Token.EQUAL, Token.LESS, Token.PLUS, Token.SUB}:
            return
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.PLUS, Token.SUB, Token.SEMI, Token.RPAREN, Token.EQUAL, Token.LESS, Token.DIV, Token.MULT])


    def p_unit(self):
        if self.peek.token == Token.NUM:
            self.peek = self.scanner.token()
        elif self.peek.token == Token.ID:
            if self.useSymbol:
                if self.ST.lookup(self.peek.value) == None:
                    raise SymbolTableException(self.scanner.get_lineno(),self.peek.value)
            self.peek = self.scanner.token()
        elif self.peek.token == Token.LPAREN:
            self.peek = self.scanner.token()
            self.p_expr()
            self.match(Token.RPAREN)
        else:
            raise ParserException(self.scanner.get_lineno(), self.peek, [Token.NUM, Token.ID, Token.LPAREN])
