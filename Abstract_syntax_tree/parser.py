
import pdb
from C_ast import *
from typing import Callable,List,Tuple,Optional
from scanner import Lexeme,Token,Scanner

class IDType(Enum):
    IO = 1
    VAR = 2
	
class SymbolTableData:
    def __init__(self, id_type: IDType, data_type: Type, new_name: str) -> None:
        self.id_type = id_type      
                                    
        self.data_type = data_type  
                                    
        self.new_name = new_name    

    def get_id_type(self) -> IDType:
        return self.id_type

    def get_data_type(self) -> Type:
        return self.data_type

    def get_new_name(self) -> str:
        return self.new_name

class SymbolTableException(Exception):
    def __init__(self, lineno: int, ID: str) -> None:
        message = "Symbol table error on line: " + str(lineno) + "\nUndeclared ID: " + str(ID)
        super().__init__(message)
	
class NewLabelGenerator():
    def __init__(self) -> None:
        self.counter = 0
        
    def mk_new_label(self) -> str:
        new_label = "label" + str(self.counter)
        self.counter += 1
        return new_label

class NewNameGenerator():
    def __init__(self) -> None:
        self.counter = 0
        self.new_names = []

    def mk_new_name(self) -> str:
        new_name = "_new_name" + str(self.counter)
        self.counter += 1
        self.new_names.append(new_name)
        return new_name

class VRAllocator():
    def __init__(self) -> None:
        self.counter = 0
        
    def mk_new_vr(self) -> str:
        vr = "vr" + str(self.counter)
        self.counter += 1
        return vr

    def declare_variables(self) -> List[str]:
        ret = []
        for i in range(self.counter):
            ret.append("virtual_reg vr%d;" % i)

        return ret


class SymbolTable:
	#added NewNameGenerator to add new names in Symbol table
    def __init__(self, new_name_generator: NewNameGenerator) -> None:

        self.ht_stack = [dict()]
        self.new_name_generator = new_name_generator

    def insert(self, ID: str, id_type: IDType, data_type: Type) -> None:
	#if it's a VAR type create new name
        if id_type == IDType.VAR:

            new_name = self.new_name_generator.mk_new_name()
        else:
            new_name = ID

        info = SymbolTableData(id_type, data_type, new_name)
        self.ht_stack[-1][ID] = info



    def lookup(self, ID: str) -> Optional:
        for ht in reversed(self.ht_stack):
            if ID in ht:
                return ht[ID]
        return None

    def push_scope(self) -> None:
        self.ht_stack.append(dict())

    def pop_scope(self) -> None:
        self.ht_stack.pop()


class ParserException(Exception):

    def __init__(self, lineno: int, lexeme: Lexeme, tokens: List[Token]) -> None:
        message = "Parser error on line: " + str(lineno) + "\nExpected one of: " + str(tokens) + "\nGot: " + str(lexeme)
        super().__init__(message)


class Parser:


    def __init__(self, scanner: Scanner) -> None:
        
        self.scanner = scanner


        self.vra = VRAllocator()
        self.nlg = NewLabelGenerator()
        self.nng = NewNameGenerator()


        self.symbol_table = SymbolTable(self.nng)

        self.function_name = None
        self.function_args = []

    def parse(self, s: str) -> List[str]:

        self.scanner.input_string(s)
        self.to_match = self.scanner.token()

        p = self.parse_function()
        self.eat(None)
        
        return p

    def get_token_id(self, l: Lexeme) ->Token:
        if l is None:
            return None
        return l.token


    def eat(self, check: Token) -> None:
        token_id = self.get_token_id(self.to_match)
        if token_id != check:
            raise ParserException(self.scanner.get_lineno(),
                                  self.to_match,
                                  [check])      
        self.to_match = self.scanner.token()


    def parse_function(self) -> List[str]:

        self.parse_function_header()    
        self.eat(Token.LBRACE)


        p = self.parse_statement_list()        
        self.eat(Token.RBRACE)
        return p


    def parse_function_header(self) -> None:
        self.eat(Token.VOID)
        function_name = self.to_match.value
        self.eat(Token.ID)        
        self.eat(Token.LPAR)
        self.function_name = function_name
        args = self.parse_arg_list()
        self.function_args = args
        self.eat(Token.RPAR)


    def parse_arg_list(self) -> List[Tuple[str, str]]:
        token_id = self.get_token_id(self.to_match)
        if token_id == Token.RPAR:
            return
        arg = self.parse_arg()
        token_id = self.get_token_id(self.to_match)
        if token_id == Token.RPAR:
            return [arg]
        self.eat(Token.COMMA)
        arg_l = self.parse_arg_list()
        return arg_l + [arg]

    def parse_arg(self) -> Tuple[str, str]:
        token_id = self.get_token_id(self.to_match)
        if token_id == Token.FLOAT:
            self.eat(Token.FLOAT)
            data_type = Type.FLOAT
            data_type_str = "float"            
        elif token_id == Token.INT:
            self.eat(Token.INT)
            data_type = Type.INT
            data_type_str = "int"
        else:
            raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              [Token.INT, Token.FLOAT])
        self.eat(Token.AMP)

        id_name = self.to_match.value
        self.eat(Token.ID)

        self.symbol_table.insert(id_name, IDType.IO, data_type)
        return (id_name, data_type_str)

    def parse_statement_list(self) -> List[str]:
        three_addr_codes = []
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.INT, Token.FLOAT, Token.ID, Token.IF, Token.LBRACE, Token.FOR]:
            three_addr_codes += self.parse_statement()
            three_addr_codes += self.parse_statement_list()
            return three_addr_codes
        if token_id in [Token.RBRACE]:
            return three_addr_codes

    def parse_statement(self) -> List[str]:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.INT, Token.FLOAT]:
            return self.parse_declaration_statement()
        elif token_id in [Token.ID]:
            return self.parse_assignment_statement()
        elif token_id in [Token.IF]:
            return self.parse_if_else_statement()
        elif token_id in [Token.LBRACE]:
            return self.parse_block_statement()
        elif token_id in [Token.FOR]:
            return self.parse_for_statement()
        else:
            raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              [Token.FOR, Token.IF, Token.LBRACE, Token.INT, Token.FLOAT, Token.ID])










	#doesn't return anything just insert new variables if never found in scope
    def parse_declaration_statement(self) -> List[str]:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.INT]:
            self.eat(Token.INT)
            id_name = self.to_match.value

            if self.symbol_table.lookup(id_name) == None:
                self.symbol_table.insert(id_name, IDType.VAR, Type.INT)

            self.eat(Token.ID)
            self.eat(Token.SEMI)

            return []

        if token_id in [Token.FLOAT]:
            self.eat(Token.FLOAT)
            id_name = self.to_match.value

            if self.symbol_table.lookup(id_name) == None:
                self.symbol_table.insert(id_name, IDType.VAR, Type.FLOAT)

            self.eat(Token.ID)
            self.eat(Token.SEMI)


            return []
        
        raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              [Token.INT, Token.FLOAT])

 
    def parse_assignment_statement(self) -> List[str]:
        ast = self.parse_assignment_statement_base()
        self.eat(Token.SEMI)
        return ast

 
    def parse_assignment_statement_base(self) -> List[str]:
        id_name = self.to_match.value
        id_data = self.symbol_table.lookup(id_name)
        if id_data == None:
            raise SymbolTableException(self.scanner.get_lineno(), id_name)

        self.eat(Token.ID)
        self.eat(Token.ASSIGN)
        ast = self.parse_expr()
        type_inference(ast, self.vra)

        program = linearize_ast(ast)
	#logic to check if it's a new name, vr or any othe variable to correctly assign each other
        new_inst = []
        if id_data.data_type is Type.INT:
            if ast.get_type() == Type.FLOAT:
                node = ASTFloatToIntNode(ast)
                node.vr = self.vra.mk_new_vr()
                new_inst += ["%s = vr_float2int(%s);" % (node.vr, ast.vr)]
                
                if str(node.vr).startswith("vr"):
                    if str(id_data.new_name).startswith("_new_name"):
                        new_inst += ["%s = %s;" % (id_data.new_name, node.vr)]
                    else:
                        new_inst += ["%s = vr2int(%s);" % (id_data.new_name, node.vr)]
                elif str(node.vr).startswith("_new_name"):
                    if str(id_data.new_name).startswith("vr"):
                        new_inst += ["%s = %s;" % (id_data.new_name, node.vr)]
                    else:
                        new_inst += ["%s = vr2int(%s);" % (id_data.new_name, node.vr)]
                else:
                    new_inst += ["%s = vr2int(%s);" % (id_data.new_name, node.vr)]

            else:
                if str(ast.vr).startswith("vr"):
                    if str(id_data.new_name).startswith("_new_name"):
                        new_inst += ["%s = %s;" % (id_data.new_name, ast.vr)]
                    else:
                        new_inst += ["%s = vr2int(%s);" % (id_data.new_name, ast.vr)]
                elif str(ast.vr).startswith("_new_name"):
                    if str(id_data.new_name).startswith("vr"):
                        new_inst += ["%s = %s;" % (id_data.new_name, ast.vr)]
                    else:
                        new_inst += ["%s = vr2int(%s);" % (id_data.new_name, ast.vr)]
                else:
                    new_inst += ["%s = vr2int(%s);" % (id_data.new_name, ast.vr)]
                
        elif id_data.data_type is Type.FLOAT:
            if ast.get_type() == Type.INT:
                node = ASTIntToFloatNode(ast)
                node.vr = self.vra.mk_new_vr()
                new_inst += ["%s = vr_int2float(%s);" % (node.vr, ast.vr)]

                if str(node.vr).startswith("vr"):
                    if str(id_data.new_name).startswith("_new_name"):
                        new_inst += ["%s = %s;" % (id_data.new_name, node.vr)]
                    else:
                        new_inst += ["%s = vr2float(%s);" % (id_data.new_name, node.vr)]
                elif str(node.vr).startswith("_new_name"):
                    if str(id_data.new_name).startswith("vr"):
                        new_inst += ["%s = %s;" % (id_data.new_name, node.vr)]
                    else:
                        new_inst += ["%s = vr2float(%s);" % (id_data.new_name, node.vr)]
                else:
                    new_inst += ["%s = vr2float(%s);" % (id_data.new_name, node.vr)]

            else:
                if str(ast.vr).startswith("vr"):
                    if str(id_data.new_name).startswith("_new_name"):
                        new_inst += ["%s = %s;" % (id_data.new_name, ast.vr)]
                    else:
                        new_inst += ["%s = vr2float(%s);" % (id_data.new_name, ast.vr)]
                elif str(ast.vr).startswith("_new_name"):
                    if str(id_data.new_name).startswith("vr"):
                        new_inst += ["%s = %s;" % (id_data.new_name, ast.vr)]
                    else:
                        new_inst += ["%s = vr2float(%s);" % (id_data.new_name, ast.vr)]
                else:
                    new_inst += ["%s = vr2float(%s);" % (id_data.new_name, ast.vr)]

        return program + new_inst



    def parse_if_else_statement(self) -> List[str]:
        self.eat(Token.IF)
        self.eat(Token.LPAR)
        ast = self.parse_expr()

        type_inference(ast, self.vra)

        program0 = linearize_ast(ast)

        ze = self.vra.mk_new_vr()
        label = self.nlg.mk_new_label()

        instze = ["%s = int2vr(0);" % (ze)]

        instlabel = ["beq(%s,%s,%s)" % (ze, ast.vr, label)]



        self.eat(Token.RPAR)
        program1 = self.parse_statement()

        self.eat(Token.ELSE)
        program2 = self.parse_statement()
        label2 = self.nlg.mk_new_label()
        elinst = ["branch(%s)" % label2, "%s:" % label]

        finale = ["%s:" % label2]

        return program0 + instze + instlabel + program1 + elinst + program2 + finale
    

    def parse_block_statement(self) -> List[str]:
        self.eat(Token.LBRACE)
        self.symbol_table.push_scope()
        program = self.parse_statement_list()
        self.symbol_table.pop_scope()
        self.eat(Token.RBRACE)
        return program


    def parse_for_statement(self) -> List[str]:
        self.eat(Token.FOR)
        self.eat(Token.LPAR)
        program0 = self.parse_assignment_statement()

        label = self.nlg.mk_new_label()
        instlabel = ["%s:" % label]
 
        ast = self.parse_expr()
        type_inference(ast,self.vra)
        program = linearize_ast(ast)

        ze = self.vra.mk_new_vr()
        label1 = self.nlg.mk_new_label()
        instze = ["%s = int2vr(0);" % (ze)]
        branchlabel = ["beq(%s,%s,%s)" % (ze, ast.vr, label1)]

        elinst = ["branch(%s)" % label]
        finale = ["%s:" % label1]


        self.eat(Token.SEMI)
        program1 = self.parse_assignment_statement_base()

        self.eat(Token.RPAR)
        program2 = self.parse_statement()

        return program0 + instlabel + program + instze + branchlabel + program2 + program1 + elinst + finale

#if right is none return left otherwise return right
    def parse_expr(self) -> ASTNode:
        left = self.parse_comp() 
        right = self.parse_expr2(left)
        return right if right else left

#if it's there create a node and vr
    def parse_expr2(self, node) -> ASTNode:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.EQ]:
            self.eat(Token.EQ)
            right = self.parse_comp()
            result_node = ASTEqNode(node, right)
            result_node.vr = self.vra.mk_new_vr()
            return self.parse_expr2(result_node)
            
        elif token_id in [Token.SEMI, Token.RPAR]:
            return node
        raise ParserException(self.scanner.get_lineno(),
                            self.to_match,            
                            [Token.EQ, Token.SEMI, Token.RPAR])
        
    def parse_comp(self) -> ASTNode:
        left = self.parse_factor() 
        right = self.parse_comp2(left)
        return right if right else left

    def parse_comp2(self, node) -> ASTNode:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.LT]:
            self.eat(Token.LT)
            right = self.parse_factor()
            result_node = ASTLtNode(node, right)
            result_node.vr = self.vra.mk_new_vr()
            return self.parse_comp2(result_node)

        elif token_id in [Token.SEMI, Token.RPAR, Token.EQ]:
            return node
        
        raise ParserException(self.scanner.get_lineno(),
                            self.to_match,            
                            [Token.EQ, Token.SEMI, Token.RPAR, Token.LT])


    def parse_factor(self) -> ASTNode:
        left = self.parse_term()
        right = self.parse_factor2(left) 
        return right if right else left


    def parse_factor2(self,node) -> ASTNode:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.PLUS]:
            self.eat(Token.PLUS)
            right = self.parse_term()  
            
            result_node = ASTPlusNode(node, right)
            type_inference(result_node, self.vra)
















            result_node.vr = self.vra.mk_new_vr()
            return self.parse_factor2(result_node)

        elif token_id in [Token.MINUS]:
            self.eat(Token.MINUS)
            right = self.parse_term()
            result_node = ASTMinusNode(node, right)
            node.vr = self.vra.mk_new_vr()
            return self.parse_factor2(result_node)
            
        elif token_id in [Token.EQ, Token.SEMI, Token.RPAR, Token.LT]:
            return node
        raise ParserException(self.scanner.get_lineno(),
                            self.to_match,            
                            [Token.EQ, Token.SEMI, Token.RPAR, Token.LT, Token.PLUS, Token.MINUS])

    def parse_term(self) -> ASTNode:
        left = self.parse_unit() 
        right = self.parse_term2(left) 
        return right if right else left


    def parse_term2(self, node: ASTNode) -> ASTNode:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.DIV]:
            self.eat(Token.DIV)
            right = self.parse_unit() 
            result_node = ASTDivNode(node, right)
            result_node.vr = self.vra.mk_new_vr()
            return self.parse_term2(result_node) 
       
        elif token_id in [Token.MUL]:
            self.eat(Token.MUL)
            right = self.parse_unit()
            result_node = ASTMultNode(node, right)
            result_node.vr = self.vra.mk_new_vr()
            return self.parse_term2(result_node)

        elif token_id in [Token.EQ, Token.SEMI, Token.RPAR, Token.LT, Token.PLUS, Token.MINUS]:
            return node
        raise ParserException(self.scanner.get_lineno(),
                                self.to_match,            
                                [Token.EQ, Token.SEMI, Token.RPAR, Token.LT, Token.PLUS, Token.MINUS, Token.MUL, Token.DIV])


    def parse_unit(self) -> ASTNode:
        token_id = self.get_token_id(self.to_match)
        if token_id in [Token.NUM]:
            num_value = self.to_match.value 
            self.eat(Token.NUM)            
            node = ASTNumNode(num_value)
            node.vr = self.vra.mk_new_vr()
            
            return node
        elif token_id in [Token.ID]:
            id_name = self.to_match.value
            id_data = self.symbol_table.lookup(id_name)
            if id_data == None:
                raise SymbolTableException(self.scanner.get_lineno(), id_name)
            self.eat(Token.ID)
            if(id_data.id_type == IDType.IO):
                node = ASTIOIDNode(id_name, id_data.data_type)
                node.vr = self.vra.mk_new_vr()
                return node
            else:
                node = ASTVarIDNode(self.symbol_table.lookup(id_name).new_name, id_data.data_type)
                node.vr = self.vra.mk_new_vr() 
                return node
        elif token_id in [Token.LPAR]:
            self.eat(Token.LPAR)
            node = self.parse_expr() 
            self.eat(Token.RPAR)
            return node
            
        raise ParserException(self.scanner.get_lineno(),
                            self.to_match,            
                            [Token.NUM, Token.ID, Token.LPAR]) 




def is_leaf_node(node) -> bool:
    return issubclass(type(node), ASTLeafNode)

def is_UN_node(node) -> bool:
    return issubclass(type(node), ASTUnOpNode)
#check if type are same if not insert node to change type
def type_inference(node, vra: VRAllocator) -> Type:
    if is_leaf_node(node):
        return node.node_type

    if is_UN_node(node):
        return node.child.node_type

    elif isinstance(node, (ASTPlusNode, ASTMinusNode, ASTMultNode, ASTDivNode)):
        left_type = type_inference(node.l_child, vra)
        right_type = type_inference(node.r_child, vra)

        if left_type == Type.INT and right_type == Type.INT:
            node.set_type(Type.INT)
        else:
            node.set_type(Type.FLOAT)


        if left_type != right_type:
            if left_type == Type.INT and right_type == Type.FLOAT:

                node.l_child = ASTFloatToIntNode(node.l_child)
                node.l_child.vr = vra.mk_new_vr()
                node.l_child.data_type = Type.FLOAT
                
            elif left_type == Type.FLOAT and right_type == Type.INT:
                node.r_child = ASTIntToFloatNode(node.r_child)
                node.r_child.vr = vra.mk_new_vr()
                node.r_child.data_type = Type.FLOAT
            else:
                raise ParserException(self.scanner.get_lineno(), self.to_match, [Token.NUM, Token.ID, Token.LPAR]) 

        node.data_type = left_type if left_type == right_type else Type.FLOAT  
        return node.data_type
    
    elif isinstance(node, (ASTEqNode, ASTLtNode)):
        left_type = type_inference(node.l_child, vra)
        right_type = type_inference(node.r_child, vra)

        if left_type == Type.INT and right_type == Type.INT:
            node.set_type(Type.INT)
        else:
            node.set_type(Type.FLOAT)
        

        if left_type != right_type:
            if left_type == Type.INT and right_type == Type.FLOAT:
                node.l_child = ASTFloatToIntNode(node.l_child)
                node.l_child.vr = vra.mk_new_vr()
                node.l_child.data_type = Type.FLOAT

            elif left_type == Type.FLOAT and right_type == Type.INT:
                node.r_child = ASTIntToFloatNode(node.r_child)
                node.r_child.vr = vra.mk_new_vr()
                node.r_child.data_type = Type.FLOAT
            else:
                raise ParserException(self.scanner.get_lineno(), self.to_match, [Token.NUM, Token.ID, Token.LPAR]) 

        node.data_type = left_type if left_type == right_type else Type.FLOAT  
        return node.data_type
    else:
        raise Exception
