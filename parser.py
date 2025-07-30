# TODO: I need to follow the XML hiearchy

import xml.etree.ElementTree as ET

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    # PROGRAM STRUCTURE 

    def parse_class(self):
        document = ET.Element("CLASS")
        self._process(document, "KEYWORD", ["class"])
        self._process(document, "IDENTIFIER")
        self._process(document, "SYMBOL", "{")
        while self.tokenizer.peek(0)["value"] in ("static", "field"):
            pass
        while self.tokenizer.peek(0)["value"]  in ("constructor", "function", "method"):
            self.parse_subroutine_declaration(document)
        self._process(document, "SYMBOL", "}")

        return ET.tostring(document, encoding='unicode')

    def parse_subroutine_declaration(self, document):
        document = ET.SubElement(document, "subroutineDec")
        self._process(document, "KEYWORD", ["constructor", "function", "method"])
        if self.tokenizer.peek(0)["value"] == "void":
            self._process(document, "KEYWORD", ["void"])
        else:
            pass
        self.parse_subroutine_name(document)
        self._process(document, "SYMBOL", "(")
        self.parse_parameter_list(document)
        self._process(document, "SYMBOL", ")")
        self.parse_subroutine_body(document)

    def parse_subroutine_name(self, document):
        self._process(document, "IDENTIFIER")


    def parse_parameter_list(self, document):
        pass
    
    def parse_subroutine_body(self, document):
        document = ET.SubElement(document, "subroutineBody")
        self._process(document, "SYMBOL", "{")
        if self.tokenizer.peek(0)["value"] == "var":
            self.parse_variable_declaration(document)
        self.parse_statements(document)
        self._process(document, "SYMBOL", "}")

    def parse_variable_declaration(self, document):
        pass

    # STATEMENTS

    def parse_statements(self, document):
        statements_element = ET.SubElement(document, "statements")
        while self.tokenizer.peek(0)["value"] != "}":
            if self.tokenizer.peek(0)["value"] == "let":
                pass
            elif self.tokenizer.peek(0)["value"] == "if":
                pass
            elif self.tokenizer.peek(0)["value"] == "while":
                pass
            elif self.tokenizer.peek(0)["value"] == "do":
                do_statement = ET.SubElement(statements_element, "doStatement")
                self._process(do_statement, "KEYWORD", "do")
                self.parse_subroutine_call(do_statement)
                self._process(do_statement, "SYMBOL", ";")
            elif self.tokenizer.peek(0)["value"] == "return":
                return_statement = ET.SubElement(statements_element, "returnStatement")
                self._process(return_statement, "KEYWORD", "return")
                self._process(return_statement, "SYMBOL", ";")

    # EXPRESSIONS

    def parse_subroutine_call(self, document):
        if self.tokenizer.peek(1)["value"] == "[":
            pass
        elif self.tokenizer.peek(1)["value"] == "(":
            pass
        elif self.tokenizer.peek(1)["value"] == ".":
            self._process(document, "IDENTIFIER")
            self._process(document, "SYMBOL", ".")
            self._process(document, "IDENTIFIER")
            self._process(document, "SYMBOL", "(")
            self.parse_expression_list(document)
            self._process(document, "SYMBOL", ")")
    
    def parse_expression_list(self, document):
        while self.tokenizer.peek(0)["value"] != ")":
            if self.tokenizer.peek(0)["value"] == ",":
                self._process(document, "SYMBOL", ",")
            self._process(document, self.tokenizer.peek(0)["type"]) # Check if string or integer

    # PRIVATE

    def _process(self, document, expected_symbol_type=None, expected_symbol_values=None):
        token = self.tokenizer.next_token()
        if expected_symbol_type and token["type"] != expected_symbol_type:
            raise SyntaxError(f"Expected {expected_symbol_type}, got {token["type"]}")
        if token["type"] != "IDENTIFIER":
            if expected_symbol_values and not (token["value"] in expected_symbol_values):
                raise SyntaxError(f"Expected {expected_symbol_values}, got {token["value"]}")
        
        self._add_xml(document, token)

    def _add_xml(self, document, token):
        element = ET.SubElement(document, token["type"])
        element.text = token["value"]
