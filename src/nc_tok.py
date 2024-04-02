from enum import Enum, auto

KEYWORDS = "i32", "fn", "var"


class Pos:
    def __init__(self, line, col, idx, text, path):
        self.line = line
        self.col = col
        self.idx = idx
        self.text = text
        self.path = path

    def __repr__(self):
        return f"Pos({self.line}:{self.col} - {self.path})"

    def __str__(self):
        return f"{self.line}:{self.col} - {self.path}"


class TokType(Enum):
    EOF = auto()
    PLUS = auto()
    STAR = auto()
    INT = auto()
    KW = auto()
    IDENT = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_BRAKET = auto()
    CLOSE_BRAKET = auto()
    OPEN_CURLY = auto()
    CLOSE_CURLY = auto()
    SEMICOLON = auto()
    EQUALS = auto()


str_to_tok_type = {
    "+": TokType.PLUS,
    "*": TokType.STAR,
    "(": TokType.OPEN_PAREN,
    ")": TokType.CLOSE_PAREN,
    "[": TokType.OPEN_BRAKET,
    "]": TokType.CLOSE_BRAKET,
    "{": TokType.OPEN_CURLY,
    "}": TokType.CLOSE_CURLY,
    ";": TokType.SEMICOLON,
    "=": TokType.EQUALS
}


class Tok:
    def __init__(self, start: Pos, end: Pos, type_: TokType, value=None):
        self.start = start
        self.end = end
        self.type = type_
        self.value = value

    def __repr__(self):
        type_str = str(self.type).removeprefix(self.type.__class__.__name__ + ".")
        if self.value is not None:
            return f"Tok({type_str}, {self.value})"
        else:
            return f"Tok({type_str})"

    def __eq__(self, other):
        if isinstance(other, TokType):
            return self.type == other
        elif isinstance(other, tuple) or isinstance(other, list):
            return self.type == other[0] and self.value == other[1]
        elif not isinstance(other, Tok):
            return NotImplemented
        elif self.value is not None:
            return self.type == other.type and self.value == other.value
        else:
            return self.type == other.type


class LexerSyntaxError(Exception):
    def __init__(self, msg, start, end):
        super().__init__(f"Syntax Error at {start}: {msg}")
        self.start = start
        self.end = end
        self.msg = msg


class Lexer:
    def __init__(self, file_contents, file_path):
        self.text = file_contents.replace("\r\n", "\n").replace("\r", "\n")
        self.path = file_path
        self.line = 0
        self.col = 0
        self.idx = 0

    @property
    def c(self):
        if self.idx >= len(self.text):
            return None
        return self.text[self.idx]

    def pos(self, save=None):
        if save is not None:
            return Pos(*save, self.text, self.path)
        else:
            return Pos(self.line, self.col, self.idx, self.text, self.path)

    def save_pos(self):
        return self.line, self.col, self.idx

    def restore_pos(self, save):
        self.line, self.col, self.idx = save

    def advance(self):
        if self.idx >= len(self.text):
            return False

        if self.c == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        self.idx += 1
        if self.idx >= len(self.text):
            return False
        return True

    def single_char_tok(self, type_, value=None):
        save = self.save_pos()
        self.advance()
        return Tok(self.pos(save), self.pos(), type_, value)

    def parse_number(self):
        start = self.save_pos()
        num_value = self.c
        while self.advance() and self.c.isdigit():
            num_value += self.c

        return Tok(self.pos(start), self.pos(), TokType.INT, int(num_value))

    def parse_ident(self):
        start = self.save_pos()
        ident = self.c
        while self.advance() and self.c.isalnum() or self.c == "_":
            ident += self.c

        if ident in KEYWORDS:
            return Tok(self.pos(start), self.pos(), TokType.KW, ident)
        return Tok(self.pos(start), self.pos(), TokType.IDENT, ident)

    def parse_symbol(self):
        if self.c in str_to_tok_type:
            return self.single_char_tok(str_to_tok_type[self.c])
        else:
            start = self.save_pos()
            self.advance()
            raise LexerSyntaxError(f"unexpected character {self.c}", self.pos(start), self.pos())

    def get_next_token(self):
        while self.c is not None and self.c.isspace():
            if not self.advance():
                break

        if self.c is None:
            return Tok(self.pos(), self.pos(), TokType.EOF)

        if self.c in "0123456789":
            return self.parse_number()
        elif self.c.isalpha():
            return self.parse_ident()
        else:
            return self.parse_symbol()

    def get_tokens(self):
        tokens = []

        while not tokens or tokens[-1] != TokType.EOF:
            tokens.append(self.get_next_token())

        return tokens
