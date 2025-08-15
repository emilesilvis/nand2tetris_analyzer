import sys
import os
from tokenizer import Tokenizer
from parser import Parser
from compilation_engine import CompilationEngine

def process_jack_file(jack_file_path):
    with open(jack_file_path, 'r') as f:
        jack_file_contents = f.read()
    
    tokenizer = Tokenizer(jack_file_contents)
    parser = Parser(tokenizer)
    parse_tree = parser.parse_class()
    compilation_engine = CompilationEngine(parse_tree, parser.symbol_table)

    vm_output = compilation_engine.compile_class()
    
    vm_file_path = jack_file_path.replace('.jack', '.vm')
    
    with open(vm_file_path, 'w') as f:
        f.write(vm_output)
    
    print(f"Generated: {vm_file_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler.py <input_file.jack> or <directory with *.jack files>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        if input_path.endswith('.jack'):
            process_jack_file(input_path)
        else:
            print("Error: File must have .jack extension")
            sys.exit(1)

    elif os.path.isdir(input_path):
        jack_files = []
        for filename in os.listdir(input_path):
            if filename.endswith('.jack'):
                jack_file_path = os.path.join(input_path, filename)
                jack_files.append(jack_file_path)
        
        if not jack_files:
            print(f"No .jack files found in directory: {input_path}")
            sys.exit(1)
        
        for jack_file_path in jack_files:
            process_jack_file(jack_file_path)
        
        print(f"Processed {len(jack_files)} files in {input_path}")
    
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()