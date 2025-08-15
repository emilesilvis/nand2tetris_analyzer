import sys
import os
import glob
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import Tokenizer
from parser import Parser
from compilation_engine import CompilationEngine

# Find all Jack files in the Square directory
jack_files = glob.glob('tests/Square/*.jack')

for jack_file in sorted(jack_files):
    # Read and compile the Jack file
    with open(jack_file, 'r') as f:
        source = f.read()

    tokenizer = Tokenizer(source)
    parser = Parser(tokenizer)
    parse_tree = parser.parse_class()
    compilation_engine = CompilationEngine(parse_tree, parser.symbol_table)

    vm_output = compilation_engine.compile_class()
    
    # Check if there's a corresponding .vm_compare file
    compare_file = jack_file.replace('.jack', '.vm_compare')
    if os.path.exists(compare_file):
        with open(compare_file, 'r') as f:
            expected_vm = f.read()

        generated_lines = [line.strip() for line in vm_output.strip().split('\n') if line.strip()]
        expected_lines = [line.strip() for line in expected_vm.strip().split('\n') if line.strip()]

        assert generated_lines == expected_lines
        print(f"{os.path.basename(jack_file)} test passed!")
    else:
        pass

print("All Square tests completed!")
