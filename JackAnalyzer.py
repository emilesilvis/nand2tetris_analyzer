import sys
import os
from tokenizer import Tokenizer
from parser import Parser

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file.jack> or /<directory with *.jack files>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        jack_file_contents = open(input_path, 'r').read()
        tokenizer = Tokenizer(jack_file_contents)
        parser = Parser(tokenizer)
        print(parser.parse_class())

    elif os.path.isdir(input_path):
        print("directory")

if __name__ == "__main__":
    main()