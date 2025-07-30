import sys
import os
from tokenizer import Tokenizer

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file.jack> or /<directory with *.jack files>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        jack_file_contents = open(input_path, 'r').read()
        tokenizer = Tokenizer(jack_file_contents)
        for token in tokenizer.tokens:
            print(tokenizer.next_token())

    elif os.path.isdir(input_path):
        print("directory")

if __name__ == "__main__":
    main()