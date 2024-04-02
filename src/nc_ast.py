from abc import ABC
from enum import Enum, auto

from nc_tok import TokType
from static_types import TypeID


class ParserError(Exception):
    def __init__(self, msg, start, end):
        super().__init__(f"Syntax Error at {start}: {msg}")
        self.start = start
        self.end = end
        self.msg = msg


class NodeType(Enum):
    BIN_ADD = auto()
    BIN_MUL = auto()
    INT_LIT = auto()
    SCOPE = auto()
    GLOBAL_SCOPE = auto()
    VAR_DEF = auto()
    FUNC_DEF = auto()


tok_type_to_bin_node_type = {
    TokType.PLUS: NodeType.BIN_ADD,
    TokType.STAR: NodeType.BIN_MUL
}


class Node(ABC):
    def __init__(self, start, end, type_):
        self.start = start
        self.end = end
        self.type = type_

    def __repr__(self):
        attrs = [attr for attr in self.__dict__ if not attr.startswith("__") and attr not in ("start", "end", "type")]
        attr_values = [attr + '=' + repr(getattr(self, attr)) for attr in attrs]
        type_str = str(self.type).removeprefix(self.type.__class__.__name__ + ".")
        attr_values.insert(0, f"type={type_str}")
        attr_str = ', '.join(attr_values)
        return f"{self.__class__.__name__}({attr_str})"

    def __tree_list(self, ls, indent):
        indent_str = "    " * (indent + 1)
        print("[")
        for item in ls:
            print(indent_str, end="")
            if isinstance(item, Node):
                item.tree(indent + 1)
            elif isinstance(item, list) or isinstance(item, tuple):
                self.__tree_list(item, indent + 1)
            elif isinstance(item, dict):
                self.__tree_dict(item, indent + 1)
            else:
                print(repr(item))
        print("    " * indent + "]")

    def __tree_dict(self, dct, indent):
        indent_str = "    " * (indent + 1)
        print("{")
        for key in dct:
            print(indent_str + key + ": ", end="")
            value = dct[key]
            if isinstance(value, Node):
                value.tree(indent + 1)
            elif isinstance(value, list) or isinstance(value, tuple):
                self.__tree_list(value, indent + 1)
            elif isinstance(value, dict):
                self.__tree_dict(value, indent + 1)
            else:
                print(repr(value))
        print("    " * indent + "}")

    def tree(self, indent=0):
        attrs = [attr for attr in self.__dict__ if not attr.startswith("__") and attr not in ("start", "end", "type")]
        indent_str = "    " * (indent + 1)
        type_str = str(self.type).removeprefix(self.type.__class__.__name__ + ".")
        print(self.__class__.__name__ + " - " + type_str)
        for attr in attrs:
            print(indent_str + attr + ": ", end="")
            value = getattr(self, attr)
            if isinstance(value, Node):
                value.tree(indent + 1)
            elif isinstance(value, list) or isinstance(value, tuple):
                self.__tree_list(value, indent + 1)
            elif isinstance(value, dict):
                self.__tree_dict(value, indent + 1)
            else:
                print(repr(value))


class BinNode(Node):
    def __init__(self, left, right, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left = left
        self.right = right


class LiteralNode(Node):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value


class FuncDefNode(Node):
    def __init__(self, name, return_type, body, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.return_type = return_type
        self.body = body


class ScopeNode(Node):
    def __init__(self, statements, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statements = statements


class VarDefNode(Node):
    def __init__(self, name, type_id, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.type_id = type_id
        self.value = value


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0

    def advance(self):
        self.idx += 1

    @property
    def tok(self):
        if self.idx >= len(self.tokens):
            return None
        return self.tokens[self.idx]

    def parse(self):
        functions = []
        while self.tok == (TokType.KW, "fn"):
            functions.append(self.parse_function())

        if self.tok != TokType.EOF:
            raise ParserError("unexpected tok", self.tok.start, self.tok.end)
        if not functions:
            return ScopeNode(functions, self.tok.start, self.tok.end, NodeType.GLOBAL_SCOPE)
        return ScopeNode(functions, functions[0].start, functions[-1].end, NodeType.GLOBAL_SCOPE)

    def parse_function(self):
        start = self.tok.start
        self.advance()
        if self.tok != TokType.IDENT:
            raise ParserError("expected an identifier", self.tok.start, self.tok.end)
        name = self.tok.value
        self.advance()
        if self.tok != TokType.OPEN_PAREN:
            raise ParserError("expected '('", self.tok.start, self.tok.end)
        self.advance()
        if self.tok != TokType.CLOSE_PAREN:
            raise ParserError("expected ')'", self.tok.start, self.tok.end)
        self.advance()
        type_id = self.parse_type()
        body = self.parse_block()
        return FuncDefNode(name, type_id, body, start, body.end, NodeType.FUNC_DEF)

    def parse_block(self):
        if self.tok != TokType.OPEN_CURLY:
            raise ParserError("expected '{'", self.tok.start, self.tok.end)
        start = self.tok.start
        statements = []
        self.advance()
        while self.tok not in (TokType.CLOSE_CURLY, TokType.EOF):
            statements.append(self.parse_statement())
        if self.tok != TokType.CLOSE_CURLY:
            raise ParserError("expected '}'", self.tok.start, self.tok.end)
        end = self.tok.end
        self.advance()
        return ScopeNode(statements, start, end, NodeType.SCOPE)

    def parse_statement(self):
        if self.tok == TokType.OPEN_CURLY:
            return self.parse_block()
        elif self.tok == (TokType.KW, "var"):
            return self.parse_var_declaration()

    def parse_var_declaration(self):
        start = self.tok.start
        self.advance()
        if self.tok != TokType.IDENT:
            raise ParserError("expected an identifier", self.tok.start, self.tok.end)
        name = self.tok.value
        self.advance()
        type_id = self.parse_type()
        if self.tok != TokType.EQUALS:
            raise ParserError("expected '='", self.tok.start, self.tok.end)
        self.advance()
        value = self.parse_expression()
        if self.tok != TokType.SEMICOLON:
            raise ParserError("expected ';'", self.tok.start, self.tok.end)
        end = self.tok.end
        self.advance()
        return VarDefNode(name, type_id, value, start, end, NodeType.VAR_DEF)

    def parse_type(self):
        if self.tok != (TokType.KW, "i32"):
            raise ParserError("expected a type", self.tok.start, self.tok.end)
        self.advance()
        return TypeID.i32

    def parse_expression(self):
        return self.parse_bin_op(((TokType.PLUS,), (TokType.STAR,)))

    def parse_bin_op(self, op):
        accepted_toks = op[0]
        if len(op) != 1:
            left = self.parse_bin_op(op[1:])
        else:
            left = self.parse_value()

        while self.tok in accepted_toks:
            op_tok = self.tok
            self.advance()

            if len(op) != 1:
                right = self.parse_bin_op(op[1:])
            else:
                right = self.parse_value()

            left = BinNode(left, right, left.start, right.end, tok_type_to_bin_node_type[op_tok.type])
        return left

    def parse_value(self):
        if self.tok != TokType.INT:
            raise ParserError(f"expected a value", self.tok.start, self.tok.end)

        tok = self.tok
        self.advance()
        return LiteralNode(tok.value, tok.start, tok.end, NodeType.INT_LIT)
