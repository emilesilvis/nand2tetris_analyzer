import xml.etree.ElementTree as ET

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    # PROGRAM STRUCTURE 

    def parse_class(self):
        document = ET.Element("class")
        self._process(document, "keyword", ["class"])
        self._process(document, "identifier")
        self._process(document, "symbol", "{")
        while self.tokenizer.peek(0)["value"] in ("static", "field"):
            self.parse_class_variable_declaration(document)
        while self.tokenizer.peek(0)["value"]  in ("constructor", "function", "method"):
            self.parse_subroutine_declaration(document)
        self._process(document, "symbol", "}")

        return ET.tostring(document, encoding='unicode')

    def parse_class_variable_declaration(self, document):
        class_variable_declaration_element = ET.SubElement(document, "classVarDec")
        self._process(class_variable_declaration_element, "keyword", ["static", "field"])
        self.parse_type(class_variable_declaration_element)
        self._process(class_variable_declaration_element, "symbol", ";")

    def parse_type(self, document):
        while self.tokenizer.peek(0)["value"] != ";":
            if self.tokenizer.peek(0)["type"] == "keyword":
                self._process(document, "keyword", ["int", "char", "boolean"])
            else:
                self._process(document, "identifier")
            if self.tokenizer.peek(0)["value"] == ",":
                self._process(document, "symbol", ",")
            
    def parse_subroutine_declaration(self, document):
        subroutine_declaration_element = ET.SubElement(document, "subroutineDec")
        self._process(subroutine_declaration_element, "keyword", ["constructor", "function", "method"])
        if self.tokenizer.peek(0)["value"] == "void":
            self._process(subroutine_declaration_element, "keyword", ["void"])
        else:
            pass
        self.parse_subroutine_name(subroutine_declaration_element)
        self._process(subroutine_declaration_element, "symbol", "(")
        self.parse_parameter_list(subroutine_declaration_element)
        self._process(subroutine_declaration_element, "symbol", ")")
        self.parse_subroutine_body(subroutine_declaration_element)

    def parse_subroutine_name(self, document):
        self._process(document, "identifier")

    def parse_parameter_list(self, document):
        pass
    
    def parse_subroutine_body(self, document):
        subroutine_body_element = ET.SubElement(document, "subroutineBody")
        self._process(subroutine_body_element, "symbol", "{")
        print(self.tokenizer.peek(0)["value"])
        while self.tokenizer.peek(0)["value"] == "var":
            self.parse_variable_declaration(subroutine_body_element)
        self.parse_statements(subroutine_body_element)
        self._process(subroutine_body_element, "symbol", "}")

    def parse_variable_declaration(self, document):
        variable_declaration_element = ET.SubElement(document, "varDec")
        self._process(variable_declaration_element, "keyword", "var")
        self.parse_type(variable_declaration_element)
        self._process(variable_declaration_element, "symbol", ";")

    # STATEMENTS

    def parse_statements(self, document):
        statements_element = ET.SubElement(document, "statements")
        while self.tokenizer.peek(0)["value"] != "}":
            if self.tokenizer.peek(0)["value"] == "let":
                let_statement = ET.SubElement(statements_element, "letStatement")
                self._process(let_statement, "keyword", "let")
                self._process(let_statement, "identifier")
                # TODO: Handle optional expressions
                self._process(let_statement, "symbol", "=")
                self.parse_expression_list(let_statement)
                self._process(let_statement, "symbol", ";")
            elif self.tokenizer.peek(0)["value"] == "if":
                # print("if")
                pass
            elif self.tokenizer.peek(0)["value"] == "while":
                print("while")
                pass
            elif self.tokenizer.peek(0)["value"] == "do":
                print("do")
                do_statement = ET.SubElement(statements_element, "doStatement")
                self._process(do_statement, "keyword", "do")
                self.parse_subroutine_call(do_statement)
                self._process(do_statement, "symbol", ";")
            elif self.tokenizer.peek(0)["value"] == "return":
                print("return")
                return_statement = ET.SubElement(statements_element, "returnStatement")
                self._process(return_statement, "keyword", "return")
                self._process(return_statement, "symbol", ";")

    # EXPRESSIONS

    def parse_subroutine_call(self, document):
        print('boo')
        if self.tokenizer.peek(1)["value"] == "[":
            pass
        elif self.tokenizer.peek(1)["value"] == "(":
            pass
        elif self.tokenizer.peek(1)["value"] == ".":
            self._process(document, "identifier")
            self._process(document, "symbol", ".")
            self._process(document, "identifier")
            self._process(document, "symbol", "(")
            self.parse_expression_list(document)
            self._process(document, "symbol", ")")
    
    def parse_expression_list(self, document):
        while self.tokenizer.peek(0)["value"] != ")":
            if self.tokenizer.peek(0)["value"] == ",":
                self._process(document, "symbol", ",")
            if self.tokenizer.peek(0)["type"] in ("stringConstant", "integerConstant"):
                self._process(document, self.tokenizer.peek(0)["type"], self.tokenizer.peek(0)["value"])
            elif self.tokenizer.peek(0)["type"] == "identifier" and self.tokenizer.peek(1)["value"] in ("."):
                self.parse_subroutine_call(document)
            else:
                return

    # PRIVATE

    def _process(self, document, expected_symbol_type=None, expected_symbol_values=None):
        token = self.tokenizer.next_token()
        print(token) #DEBUG
        if expected_symbol_type and token["type"] != expected_symbol_type:
            raise SyntaxError(f"Expected {expected_symbol_type}, got {token["type"]}")
        if token["type"] != "identifier":
            if expected_symbol_values and not (token["value"] in expected_symbol_values):
                raise SyntaxError(f"Expected {expected_symbol_values}, got {token["value"]}")
        
        self._add_xml(document, token)

    def _add_xml(self, document, token):
        element = ET.SubElement(document, token["type"])
        element.text = token["value"]
