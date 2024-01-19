from enum import Enum

class Type(Enum):
    INT = 1
    FLOAT = 2

class ASTNode():
    def __init__(self) -> None:
        self.node_type = None
        self.vr = None

    def set_type(self, t):
        self.node_type = t

    def get_type(self):
        return self.node_type

class ASTLeafNode(ASTNode):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__()

class ASTNumNode(ASTLeafNode):
    def __init__(self, value: str) -> None:        
        super().__init__(value)
        try:
            int(value)
            self.set_type(Type.INT)
        except ValueError:
            self.set_type(Type.FLOAT)

    def three_addr_code(self):
        if self.get_type() == Type.INT:
            return "%s = int2vr(%s);" % (self.vr, self.value)
        else:
            return "%s = float2vr(%s);" % (self.vr, self.value)

            

class ASTVarIDNode(ASTLeafNode):
    def __init__(self, value: str, value_type) -> None:
        super().__init__(value)
        self.set_type(value_type)

    def three_addr_code(self):
        return "%s = %s;" % (self.vr, self.value)


class ASTIOIDNode(ASTLeafNode):
    def __init__(self, value: str, value_type) -> None:
        super().__init__(value)
        self.set_type(value_type)
    
    def three_addr_code(self):
        if self.node_type == Type.INT:
            return "%s = int2vr(%s);" % (self.vr, self.value)
        if self.node_type == Type.FLOAT:
            return "%s = float2vr(%s);" % (self.vr, self.value)

class ASTBinOpNode(ASTNode):
    def __init__(self, l_child, r_child) -> None:
        self.l_child = l_child
        self.r_child = r_child
        super().__init__()

class ASTPlusNode(ASTBinOpNode):
    def __init__(self, l_child, r_child) -> None:
        super().__init__(l_child,r_child)

    def get_op(self):
        if self.l_child.node_type is Type.INT and self.r_child.node_type is Type.INT:
            return "addi"
        else:

            return "addf"
    
    def three_addr_code(self):
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr,self.r_child.vr)

class ASTMultNode(ASTBinOpNode):
    def __init__(self, l_child, r_child) -> None:
        super().__init__(l_child,r_child)

    def get_op(self):

        if self.l_child.node_type is Type.INT and self.r_child.node_type is Type.INT:
            return "multi"
        else:
            return "multif"

    def three_addr_code(self):
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr, self.r_child.vr)


class ASTMinusNode(ASTBinOpNode):
    def __init__(self, l_child, r_child) -> None:
        super().__init__(l_child,r_child)

    def get_op(self):
        if self.l_child.node_type is Type.INT and self.r_child.node_type is Type.INT:
            return "subi"
        else:
            return "subif"
    
    def three_addr_code(self):
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr, self.r_child.vr)


class ASTDivNode(ASTBinOpNode):
    def __init__(self, l_child, r_child) ->None:
        super().__init__(l_child,r_child)

    def get_op(self):
        if self.l_child.node_type is Type.INT and self.r_child.node_type is Type.INT:
            return "divi"
        else:
            return "divif"
    
    def three_addr_code(self):
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr, self.r_child.vr)


class ASTEqNode(ASTBinOpNode):
    def __init__(self, l_child, r_child) ->None:
        self.node_type = Type.INT
        super().__init__(l_child,r_child)

    def get_op(self):
        if self.node_type is Type.INT:
            return "eq"
        else:
            return "eqf"
    
    def three_addr_code(self):
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr, self.r_child.vr)


class ASTLtNode(ASTBinOpNode):
    def __init__(self, l_child, r_child: ASTNode) -> None:
        self.node_type = Type.INT
        super().__init__(l_child,r_child)

    def get_op(self):
        if self.node_type is Type.INT:
            return "lti"
        else:
            return "ltf"
    
    def three_addr_code(self):
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr, self.r_child.vr)


class ASTUnOpNode(ASTNode):
    def __init__(self, child) -> None:
        self.child = child
        super().__init__()
        
class ASTIntToFloatNode(ASTUnOpNode):
    def __init__(self, child) -> None:
        self.set_type(Type.FLOAT)
        super().__init__(child)

    def three_addr_code(self):
        return "%s = %s(%s);" % (self.vr, "vr_int2float", self.child.vr)


class ASTFloatToIntNode(ASTUnOpNode):
    def __init__(self, child) -> None:
        self.set_type(Type.INT)
        super().__init__(child)

    def three_addr_code(self):
        return "%s = %s(%s);" % (self.vr, "vr_float2int", self.child.vr)



def linearize_ast(node) -> list[str]:
    instructions = []
    
    if isinstance(node, ASTBinOpNode):
        instructions += linearize_ast(node.l_child)
        instructions += linearize_ast(node.r_child)
        instructions.append(node.three_addr_code())
    elif isinstance(node, ASTUnOpNode):
        instructions += linearize_ast(node.child)
        instructions.append(node.three_addr_code())
    elif isinstance(node, (ASTIOIDNode, ASTVarIDNode, ASTNumNode)):

        instructions.append(node.three_addr_code())
    else:
        raise Exception(f"Node {type(node).__name__} not handled")
    return instructions
