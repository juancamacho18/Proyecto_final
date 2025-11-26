from antlr4 import *
from DSLLexer import DSLLexer
from DSLParser import DSLParser
from visitor import Visitor

def main(archivo):
    input_stream = FileStream(archivo, encoding='utf-8')
    lexer = DSLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DSLParser(stream)
    tree = parser.programa()
    
    visitor = Visitor()
    visitor.visit(tree)

if __name__ == '__main__':
    archivo = "prueba.txt"
    main(archivo)
