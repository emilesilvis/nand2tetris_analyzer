# Jack Compiler

A Jack language compiler that translates Jack programs to VM bytecode, implemented in Python for the Nand2Tetris course.

## Overview

This compiler implements the Jack language specification from "The Elements of Computing Systems" by Nisan and Schocken. It parses Jack source code and generates VM bytecode that can be executed by the VM Emulator.

## Features

- **Tokenizer**: Handles Jack syntax including string literals with symbols
- **Parser**: Builds parse trees and symbol tables
- **Compilation Engine**: Generates VM bytecode
- **Symbol Table**: Manages variable scoping and types

## Usage

```bash
# Compile a single Jack file
python JackCompiler.py file.jack

# Compile all Jack files in a directory
python JackCompiler.py directory/
```

## Tests

Run all tests:
```bash
for test in tests/test_*.py; do python "$test"; done
```

Test suites include: Average, ComplexArrays, ConvertToBin, Pong, Seven, Square.

## Project Structure

- `JackCompiler.py` - Main compiler entry point
- `tokenizer.py` - Lexical analysis
- `parser.py` - Syntax analysis and parse tree construction
- `compilation_engine.py` - VM code generation
- `symbol_table.py` - Symbol management
- `vm_code_generator.py` - VM instruction output
- `tests/` - Test programs and expected outputs

## Requirements

- Python 3.x
- No external dependencies