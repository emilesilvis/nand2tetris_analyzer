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

# Test constructor 'new' symbols
print("Constructor 'new' symbols:")
new_symbols = parser.symbol_table.subroutine_symbols["new"]["symbols"]
print(new_symbols)
assert new_symbols == {
    "aname": ("String", "argument", 0)
}

# Test method 'hello' symbols  
print("Method 'hello' symbols:")
hello_symbols = parser.symbol_table.subroutine_symbols["hello"]["symbols"]
print(hello_symbols)
assert hello_symbols == {
    "this": ("Hello", "argument", 0),
    "apunctuation": ("String", "argument", 1), 
    "punctuation": ("String", "local", 0)
}