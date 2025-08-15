import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import Tokenizer
from parser import Parser
from compilation_engine import CompilationEngine

with open('tests/ConvertToBin/Main.jack', 'r') as f:
    source = f.read()

tokenizer = Tokenizer(source)
parser = Parser(tokenizer)
parse_tree = parser.parse_class()
compilation_engine = CompilationEngine(parse_tree, parser.symbol_table)

vm_output = compilation_engine.compile_class()

with open('tests/ConvertToBin/Main.vm_compare', 'r') as f:
    expected_vm = f.read()

generated_lines = [line.strip() for line in vm_output.strip().split('\n') if line.strip()]
expected_lines = [line.strip() for line in expected_vm.strip().split('\n') if line.strip()]

assert generated_lines == expected_lines
print("ConvertToBin test passed!")
