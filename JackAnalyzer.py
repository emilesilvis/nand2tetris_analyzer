import sys
import os
import xml.etree.ElementTree as ET
from tokenizer import Tokenizer
from parser import Parser

def parse_tree_to_xml(parse_tree_node):
    element = ET.Element(parse_tree_node.type)
    
    if parse_tree_node.value is not None and not parse_tree_node.children:
        element.text = " " + str(parse_tree_node.value) + " "
    elif not parse_tree_node.children:
        element.text = "\n" # To handle empty non-terminal nodes
    
    # Add children recursively
    for child in parse_tree_node.children:
        child_element = parse_tree_to_xml(child)
        element.append(child_element)
    
    return element

def parse_tree_to_xml_string(parse_tree_node):
    xml_element = parse_tree_to_xml(parse_tree_node)
    _indent_xml(xml_element)
    return ET.tostring(xml_element, encoding='unicode')

def _indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            _indent_xml(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def process_jack_file(jack_file_path):
    with open(jack_file_path, 'r') as f:
        jack_file_contents = f.read()
    
    tokenizer = Tokenizer(jack_file_contents)
    parser = Parser(tokenizer)
    parse_tree_root = parser.parse_class()
    xml_output = parse_tree_to_xml_string(parse_tree_root)
    
    xml_file_path = jack_file_path.replace('.jack', '.xml')
    
    with open(xml_file_path, 'w') as f:
        f.write(xml_output)
    
    print(f"Generated: {xml_file_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py <input_file.jack> or <directory with *.jack files>")
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