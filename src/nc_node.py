from abc import ABC as _ABC
from enum import Enum as _Enum, auto as _auto
from typing import Any, Sequence

from nc_tok import TokType as _TokType, Pos as _Pos
from nc_types import NCType


class NodeType(_Enum):
    BIN_ADD = _auto()
    BIN_MUL = _auto()
    INT_LIT = _auto()
    SCOPE = _auto()
    GLOBAL_SCOPE = _auto()
    VAR_DEF = _auto()
    FUNC_DEF = _auto()


tok_type_to_bin_node_type = {
    _TokType.PLUS: NodeType.BIN_ADD,
    _TokType.STAR: NodeType.BIN_MUL
}


class Node(_ABC):
    def __init__(self, start: _Pos, end: _Pos, type_: NodeType):
        self.start: _Pos = start
        self.end: _Pos = end
        self.type: NodeType = type_

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
    def __init__(self, left: Node, right: Node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left: Node = left
        self.right: Node = right


class LiteralNode(Node):
    def __init__(self, value: Any, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value: Any = value


class FuncDefNode(Node):
    def __init__(self, name: str, return_type: NCType, body: Node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.return_type: NCType = return_type
        self.body: Node = body


class ScopeNode(Node):
    def __init__(self, statements: Sequence[Node], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statements: Sequence[Node] = statements


class VarDefNode(Node):
    def __init__(self, name: str, type_id: NCType, value: Node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.type_id: NCType = type_id
        self.value: Node = value
