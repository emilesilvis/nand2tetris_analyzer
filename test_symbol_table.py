from tokenizer import Tokenizer
from parser import Parser
from symbol_table import SymbolTable


# Read Hello.jack
with open('tests/HelloWorld/Hello.jack', 'r') as f:
    source = f.read()

# Parse and check symbol table
tokenizer = Tokenizer(source)
parser = Parser(tokenizer)
parser.parse_class()

print("Class symbols:")
print(parser.symbol_table.class_symbols)
assert parser.symbol_table.class_symbols == {
    "name": ("String", "this", 0)
}

print("Subroutine symbols:")
print(parser.symbol_table.subroutine_symbols)
assert parser.symbol_table.subroutine_symbols == {
    "aname": ('String', 'argument', 0), 'apunctuation': ('String', 'argument', 1), 'punctuation': ('String', 'local', 0)
}
 
print("Indices:")
print(parser.symbol_table.indices)
assert parser.symbol_table.indices == {'static': 0, 'this': 1, 'argument': 2, 'local': 1}