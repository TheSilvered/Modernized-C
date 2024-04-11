from nc_tok import TokType
from nc_types import NCInt, NCMut
from nc_node import *


class ParserError(Exception):
    def __init__(self, msg, start, end):
        super().__init__(f"Syntax Error at {start}: {msg}")
        self.start = start
        self.end = end
        self.msg = msg


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
        return NCInt(False, 4, NCMut.READONLY)

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
