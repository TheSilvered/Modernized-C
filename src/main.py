from nc_tok import Lexer
from nc_ast import Parser
from nc_transpiler import Transpiler

out_file = "out.nc"

with open("test_file.mc") as f:
    contents = f.read()

lexer = Lexer(contents, "test_file.mc")
tokens = lexer.get_tokens()
# print(tokens)

parser = Parser(tokens)
node = parser.parse()
# node.tree()

transpiler = Transpiler(node)
text = transpiler.compile()
print(text)
