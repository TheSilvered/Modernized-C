from io import StringIO, IOBase, SEEK_SET

from nc_node import *


class Transpiler:
    def __init__(self, root_node):
        self.root_node = root_node
        self.indent = 0
        self.indent_str = "    "
        self.out_file: IOBase | None = None
        self.__last_char = ""

    def compile(self, out_file: IOBase | None = None) -> None | str:
        if out_file is None:
            self.out_file = StringIO()
        else:
            self.out_file = out_file

        if not self.out_file.writable():
            raise IOError("out_file is not writable")
        self.__last_char = ""
        self.__compile_node(self.root_node)

        if out_file is None:
            self.out_file.seek(0, SEEK_SET)
            text = self.out_file.read()
            self.out_file = None
            return text
        else:
            self.out_file = None

    def __indent(self):
        self.indent += 1

    def __dedent(self):
        self.indent -= 1
        if self.indent < 0:
            self.indent = 0

    def __append(self, text: str):
        if not text:
            return

        lines = text.split("\n")

        if self.__last_char == "\n" and lines[0]:
            self.out_file.write(self.indent_str * self.indent)

        self.out_file.write(lines[0])
        if len(lines) == 1:
            self.__last_char = text[-1]
            return

        self.out_file.write("\n")
        for line in lines[1:-1]:
            if not line:
                self.out_file.write("\n")
            else:
                self.out_file.write(self.indent_str * self.indent + line + "\n")

        if lines[-1]:
            self.out_file.write(self.indent_str * self.indent + lines[-1])

        self.__last_char = text[-1]

    def __new_line(self):
        if self.__last_char != "\n" and self.__last_char:
            self.out_file.write("\n")
            self.__last_char = "\n"

    def __compile_node(self, node):
        match node:
            case BinNode():
                self.__compile_bin_node(node)
            case LiteralNode():
                self.__compile_literal_node(node)
            case FuncDefNode():
                self.__compile_func_def_node(node)
            case ScopeNode():
                self.__compile_scope_node(node)
            case VarDefNode():
                self.__compile_var_def_node(node)
            case _:
                raise TypeError(f"compilation for {node.type} not defined")

    def __compile_bin_node(self, node: BinNode):
        self.__compile_node(node.left)
        self.__append(" ")
        match node.type:
            case NodeType.BIN_ADD:
                self.__append("+")
            case NodeType.BIN_MUL:
                self.__append("*")
        self.__append(" ")
        self.__compile_node(node.right)

    def __compile_literal_node(self, node: LiteralNode):
        self.__append(str(node.value))

    def __compile_func_def_node(self, node: FuncDefNode):
        self.__new_line()
        self.__append(node.return_type.ret_c_type())
        self.__append(" " + node.name + "() {\n")
        self.__indent()
        self.__compile_node(node.body)
        self.__dedent()
        self.__new_line()
        self.__append("}\n")

    def __compile_scope_node(self, node: ScopeNode):
        for n in node.statements:
            self.__compile_node(n)
            self.__new_line()

    def __compile_var_def_node(self, node: VarDefNode):
        self.__append(node.type_id.var_c_type() + " " + node.name + " = ")
        self.__compile_node(node.value)
        self.__append(";")
