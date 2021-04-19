from antlr4 import *
from CalcLexer import CalcLexer
from CalcParser import CalcParser
from Codegen import *

f = open("test.mylang", "r")
txt = f.read()

lexer = CalcLexer(InputStream(txt))
stream = CommonTokenStream(lexer)
parser = CalcParser(stream)

tree = parser.program()

codegen = Codegen()

ir = codegen.root(tree)
print(str(ir))