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

        ET.indent(document, space="  ")
        return ET.tostring(document, encoding='unicode')

    def parse_class_variable_declaration(self, document):
        class_variable_declaration_element = ET.SubElement(document, "classVarDec")
        self._process(class_variable_declaration_element, "keyword", ["static", "field"])
        self.parse_type_and_variables(class_variable_declaration_element)
        self._process(class_variable_declaration_element, "symbol", ";")

    def parse_type_and_variables(self, document):
        """Parse: type varName (',' varName)*"""
        # Parse the type first
        if self.tokenizer.peek(0)["type"] == "keyword":
            self._process(document, "keyword", ["int", "char", "boolean"])
        else:
            self._process(document, "identifier")  # className
        
        # Parse first variable name
        self._process(document, "identifier")
        
        # Parse additional variables: (',' varName)*
        while self.tokenizer.peek(0)["value"] == ",":
            self._process(document, "symbol", ",")
            self._process(document, "identifier")
            
    def parse_subroutine_declaration(self, document):
        subroutine_declaration_element = ET.SubElement(document, "subroutineDec")
        self._process(subroutine_declaration_element, "keyword", ["constructor", "function", "method"])
        if self.tokenizer.peek(0)["value"] == "void":
            self._process(subroutine_declaration_element, "keyword", ["void"])
        else:
            self.parse_single_type(subroutine_declaration_element)
        self.parse_subroutine_name(subroutine_declaration_element)
        self._process(subroutine_declaration_element, "symbol", "(")
        self.parse_parameter_list(subroutine_declaration_element)
        self._process(subroutine_declaration_element, "symbol", ")")
        self.parse_subroutine_body(subroutine_declaration_element)

    def parse_subroutine_name(self, document):
        self._process(document, "identifier")

    def parse_parameter_list(self, document):
        parameter_list_element = ET.SubElement(document, "parameterList")
        parameter_list_element.text = "\n"
        
        if self.tokenizer.peek(0)["value"] != ")":
            self.parse_single_type(parameter_list_element)
            self._process(parameter_list_element, "identifier") 
            
            while self.tokenizer.peek(0)["value"] == ",":
                self._process(parameter_list_element, "symbol", ",")
                self.parse_single_type(parameter_list_element)
                self._process(parameter_list_element, "identifier") 
   
    def parse_single_type(self, document):
        current_token = self.tokenizer.peek(0)
        
        if current_token["value"] in ("int", "char", "boolean"):
            self._process(document, "keyword", current_token["value"])
        elif current_token["type"] == "identifier":
            self._process(document, "identifier")

    def parse_subroutine_body(self, document):
        subroutine_body_element = ET.SubElement(document, "subroutineBody")
        self._process(subroutine_body_element, "symbol", "{")
        while self.tokenizer.peek(0)["value"] == "var":
            self.parse_variable_declaration(subroutine_body_element)
        self.parse_statements(subroutine_body_element)
        self._process(subroutine_body_element, "symbol", "}")

    def parse_variable_declaration(self, document):
        variable_declaration_element = ET.SubElement(document, "varDec")
        self._process(variable_declaration_element, "keyword", "var")
        self.parse_type_and_variables(variable_declaration_element)
        self._process(variable_declaration_element, "symbol", ";")

    # STATEMENTS

    def parse_statements(self, document):
        statements_element = ET.SubElement(document, "statements")
        while self.tokenizer.peek(0)["value"] != "}":
            if self.tokenizer.peek(0)["value"] == "let":
                let_statement = ET.SubElement(statements_element, "letStatement")
                self._process(let_statement, "keyword", "let")
                if self.tokenizer.peek(1)["value"] == "[":
                    self._process(let_statement, "identifier")
                    self._process(let_statement, "symbol", "[")
                    self.parse_expression(let_statement)
                    self._process(let_statement, "symbol", "]")
                else:
                    self._process(let_statement, "identifier")
                self._process(let_statement, "symbol", "=")
                self.parse_expression(let_statement)
                self._process(let_statement, "symbol", ";")
            elif self.tokenizer.peek(0)["value"] == "if":
                if_statement = ET.SubElement(statements_element, "ifStatement")
                self._process(if_statement, "keyword", "if")
                self._process(if_statement, "symbol", "(")
                self.parse_expression(if_statement)
                self._process(if_statement, "symbol", ")")
                self._process(if_statement, "symbol", "{")
                self.parse_statements(if_statement)
                self._process(if_statement, "symbol", "}")
                if self.tokenizer.peek(0)["value"] == "else":
                    self._process(if_statement, "keyword", "else")
                    self._process(if_statement, "symbol", "{")
                    self.parse_statements(if_statement)
                    self._process(if_statement, "symbol", "}")
            elif self.tokenizer.peek(0)["value"] == "while":
                while_statement = ET.SubElement(statements_element, "whileStatement")
                self._process(while_statement, "keyword", "while")
                self._process(while_statement, "symbol", "(")
                self.parse_expression(while_statement)
                self._process(while_statement, "symbol", ")")
                self._process(while_statement, "symbol", "{")
                self.parse_statements(while_statement)
                self._process(while_statement, "symbol", "}")
            elif self.tokenizer.peek(0)["value"] == "do":
                do_statement = ET.SubElement(statements_element, "doStatement")
                self._process(do_statement, "keyword", "do")
                self.parse_subroutine_call(do_statement)
                self._process(do_statement, "symbol", ";")
            elif self.tokenizer.peek(0)["value"] == "return":
                return_statement = ET.SubElement(statements_element, "returnStatement")
                self._process(return_statement, "keyword", "return")
                if self.tokenizer.peek(0)["value"] != ";":
                    self.parse_expression(return_statement)
                self._process(return_statement, "symbol", ";")

    # EXPRESSIONS

    def parse_subroutine_call(self, document):
        if self.tokenizer.peek(1)["value"] == "[":
            self._process(document, "identifier")
            self._process(document, "symbol", "[")
            self.parse_expression(document)
            self._process(document, "symbol", "]")
        elif self.tokenizer.peek(1)["value"] == "(":
            self._process(document, "identifier")
            self._process(document, "symbol", "(")
            self.parse_expression_list(document)
            self._process(document, "symbol", ")")
        elif self.tokenizer.peek(1)["value"] == ".":
            self._process(document, "identifier")
            self._process(document, "symbol", ".")
            self._process(document, "identifier")
            self._process(document, "symbol", "(")
            self.parse_expression_list(document)
            self._process(document, "symbol", ")")
    
    def parse_expression_list(self, document):
        expression_list_element = ET.SubElement(document, "expressionList")
        expression_list_element.text = "\n" 
        
        if self.tokenizer.peek(0)["value"] != ")":
            self.parse_expression(expression_list_element)
            
            while self.tokenizer.peek(0)["value"] == ",":
                self._process(expression_list_element, "symbol", ",")
                self.parse_expression(expression_list_element)

    def parse_expression(self, document):
        expression_element = ET.SubElement(document, "expression")
        
        self.parse_term(expression_element)
        
        while self.tokenizer.peek(0)["value"] in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            self._process(expression_element, "symbol", self.tokenizer.peek(0)["value"])
            self.parse_term(expression_element)

    def parse_term(self, document):
        term_element = ET.SubElement(document, "term")
        
        if self.tokenizer.peek(0)["type"] in ("stringConstant", "integerConstant"):
            self._process(term_element, self.tokenizer.peek(0)["type"], self.tokenizer.peek(0)["value"])
        elif self.tokenizer.peek(0)["type"] == "identifier":
            if self.tokenizer.peek(1)["value"] == "[":  
                self._process(term_element, "identifier")
                self._process(term_element, "symbol", "[")
                self.parse_expression(term_element)  
                self._process(term_element, "symbol", "]")
            elif self.tokenizer.peek(1)["value"] == ".":  
                self.parse_subroutine_call(term_element)
            else:  
                self._process(term_element, "identifier")
        elif self.tokenizer.peek(0)["value"] in ("true", "false", "null", "this"):
            self._process(term_element, "keyword", self.tokenizer.peek(0)["value"])
        elif self.tokenizer.peek(0)["value"] == "(":  
            self._process(term_element, "symbol", "(")
            self.parse_expression(term_element)
            self._process(term_element, "symbol", ")")
        elif self.tokenizer.peek(0)["value"] in ("-", "~"):  
            self._process(term_element, "symbol", self.tokenizer.peek(0)["value"])
            self.parse_term(term_element)

    # PRIVATE

    def _process(self, document, expected_symbol_type=None, expected_symbol_values=None):
        token = self.tokenizer.next_token()
        if expected_symbol_type and token["type"] != expected_symbol_type:
            raise SyntaxError(f"Expected {expected_symbol_type}, got {token["type"]}")
        if token["type"] != "identifier":
            if expected_symbol_values and not (token["value"] in expected_symbol_values):
                raise SyntaxError(f"Expected {expected_symbol_values}, got {token["value"]}")
        
        self._add_xml(document, token)

    def _add_xml(self, document, token):
        element = ET.SubElement(document, token["type"])
        element.text = " " + token["value"] + " "
