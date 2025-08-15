from parse_tree_node import ParseTreeNode
from symbol_table import SymbolTable

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.symbol_table = SymbolTable()

    # PROGRAM STRUCTURE 

    def parse_class(self):
        class_node = ParseTreeNode("class", None)
        self._process(class_node, "keyword", ["class"])

        class_name = self.tokenizer.peek(0)["value"]
        self._process(class_node, "identifier")
        self._process(class_node, "symbol", "{")
        while self.tokenizer.peek(0)["value"] in ("static", "field"):
            self.parse_class_variable_declaration(class_node)
        while self.tokenizer.peek(0)["value"]  in ("constructor", "function", "method"):
            self.parse_subroutine_declaration(class_node, class_name)
        self._process(class_node, "symbol", "}")

        return class_node

    def parse_class_variable_declaration(self, parent_node):
        class_var_dec_node = ParseTreeNode("classVarDec", None)
        parent_node.add_child(class_var_dec_node)

        # Caputre and process kind
        var_kind = self.tokenizer.peek(0)["value"]
        self._process(class_var_dec_node, "keyword", ["static", "field"])

        # Capture type
        token_type = self.tokenizer.peek(0)
        if token_type["type"] == "keyword":
            var_type = token_type["value"]  # int, char, boolean
        else:
            var_type = token_type["value"]  # className

        # Process type and variables with captured symbol information
        self.parse_type_and_variables(class_var_dec_node, var_type, var_kind)
        self._process(class_var_dec_node, "symbol", ";")

    def parse_type_and_variables(self, parent_node, var_type=None, var_kind=None):
        # Parse the type first
        if self.tokenizer.peek(0)["type"] == "keyword":
            self._process(parent_node, "keyword", ["int", "char", "boolean"])
        else:
            self._process(parent_node, "identifier")  # className
        
        # Parse first variable name
        if var_type and var_kind:
            var_name = self.tokenizer.peek(0)["value"]
            if var_kind in ("static", "field"):
                self.symbol_table.add_class_symbol(var_name, var_type, var_kind)
            else:
                self.symbol_table.add_subroutine_symbol(var_name, var_type, var_kind)
        self._process(parent_node, "identifier")
        
        # Parse additional variables: (',' varName)*
        while self.tokenizer.peek(0)["value"] == ",":
            self._process(parent_node, "symbol", ",")
            if var_type and var_kind:
                var_name = self.tokenizer.peek(0)["value"]
                if var_kind in ("static", "field"):
                    self.symbol_table.add_class_symbol(var_name, var_type, var_kind)
                else:
                    self.symbol_table.add_subroutine_symbol(var_name, var_type, var_kind)
            self._process(parent_node, "identifier")
            
    def parse_subroutine_declaration(self, parent_node, class_name):
        subroutine_dec_node = ParseTreeNode("subroutineDec", None)
        parent_node.add_child(subroutine_dec_node)
        
        subroutine_type = self.tokenizer.peek(0)["value"]
        self._process(subroutine_dec_node, "keyword", ["constructor", "function", "method"])

        if self.tokenizer.peek(0)["value"] == "void":
            self._process(subroutine_dec_node, "keyword", ["void"])
        else:
            self.parse_single_type(subroutine_dec_node)
        
        # Capture subroutine name and initialize subroutine in symbol table
        subroutine_name = self.tokenizer.peek(0)["value"]
        self.symbol_table.add_subroutine(subroutine_name)
        self.parse_subroutine_name(subroutine_dec_node)
        
        # Add 'this' parameter for methods
        if subroutine_type == "method":
            self.symbol_table.add_subroutine_symbol("this", class_name, "arg")
        self._process(subroutine_dec_node, "symbol", "(")
        self.parse_parameter_list(subroutine_dec_node)
        self._process(subroutine_dec_node, "symbol", ")")
        self.parse_subroutine_body(subroutine_dec_node)

    def parse_subroutine_name(self, parent_node):
        self._process(parent_node, "identifier")

    def parse_parameter_list(self, parent_node):
        parameter_list_node = ParseTreeNode("parameterList", None)
        parent_node.add_child(parameter_list_node)
        
        if self.tokenizer.peek(0)["value"] != ")":
            token_type = self.tokenizer.peek(0)
            if token_type["type"] == "keyword":
                param_type = token_type["value"]  # int, char, boolean
            else:
                param_type = token_type["value"]  # className

            self.parse_single_type(parameter_list_node)

            param_name = self.tokenizer.peek(0)["value"]
            self._process(parameter_list_node, "identifier")
            
            self.symbol_table.add_subroutine_symbol(param_name, param_type, "arg")
            
            while self.tokenizer.peek(0)["value"] == ",":
                self._process(parameter_list_node, "symbol", ",")

                token_type = self.tokenizer.peek(0)
                if token_type["type"] == "keyword":
                    param_type = token_type["value"]  # int, char, boolean
                else:
                    param_type = token_type["value"]  # className

                self.parse_single_type(parameter_list_node)

                param_name = self.tokenizer.peek(0)["value"]
                self._process(parameter_list_node, "identifier")

                self.symbol_table.add_subroutine_symbol(param_name, param_type, "arg")
   
    def parse_single_type(self, parent_node):
        current_token = self.tokenizer.peek(0)
        
        if current_token["value"] in ("int", "char", "boolean"):
            self._process(parent_node, "keyword", current_token["value"])
        elif current_token["type"] == "identifier":
            self._process(parent_node, "identifier")

    def parse_subroutine_body(self, parent_node):
        subroutine_body_node = ParseTreeNode("subroutineBody", None)
        parent_node.add_child(subroutine_body_node)
        self._process(subroutine_body_node, "symbol", "{")
        while self.tokenizer.peek(0)["value"] == "var":
            self.parse_variable_declaration(subroutine_body_node)
        self.parse_statements(subroutine_body_node)
        self._process(subroutine_body_node, "symbol", "}")

    def parse_variable_declaration(self, parent_node):
        var_dec_node = ParseTreeNode("varDec", None)
        parent_node.add_child(var_dec_node)
        self._process(var_dec_node, "keyword", "var")

        token_type = self.tokenizer.peek(0)
        if token_type["type"] == "keyword":
            var_type = token_type["value"]  # int, char, boolean
        else:
            var_type = token_type["value"]  # className

        self.parse_type_and_variables(var_dec_node, var_type, "var")
        self._process(var_dec_node, "symbol", ";")

    # STATEMENTS

    def parse_statements(self, parent_node):
        statements_node = ParseTreeNode("statements", None)
        parent_node.add_child(statements_node)
        while self.tokenizer.peek(0)["value"] != "}":
            if self.tokenizer.peek(0)["value"] == "let":
                let_statement_node = ParseTreeNode("letStatement", None)
                statements_node.add_child(let_statement_node)
                self._process(let_statement_node, "keyword", "let")
                if self.tokenizer.peek(1)["value"] == "[":
                    self._process(let_statement_node, "identifier")
                    self._process(let_statement_node, "symbol", "[")
                    self.parse_expression(let_statement_node)
                    self._process(let_statement_node, "symbol", "]")
                else:
                    self._process(let_statement_node, "identifier")
                self._process(let_statement_node, "symbol", "=")
                self.parse_expression(let_statement_node)
                self._process(let_statement_node, "symbol", ";")
            elif self.tokenizer.peek(0)["value"] == "if":
                if_statement_node = ParseTreeNode("ifStatement", None)
                statements_node.add_child(if_statement_node)
                self._process(if_statement_node, "keyword", "if")
                self._process(if_statement_node, "symbol", "(")
                self.parse_expression(if_statement_node)
                self._process(if_statement_node, "symbol", ")")
                self._process(if_statement_node, "symbol", "{")
                self.parse_statements(if_statement_node)
                self._process(if_statement_node, "symbol", "}")
                if self.tokenizer.peek(0)["value"] == "else":
                    self._process(if_statement_node, "keyword", "else")
                    self._process(if_statement_node, "symbol", "{")
                    self.parse_statements(if_statement_node)
                    self._process(if_statement_node, "symbol", "}")
            elif self.tokenizer.peek(0)["value"] == "while":
                while_statement_node = ParseTreeNode("whileStatement", None)
                statements_node.add_child(while_statement_node)
                self._process(while_statement_node, "keyword", "while")
                self._process(while_statement_node, "symbol", "(")
                self.parse_expression(while_statement_node)
                self._process(while_statement_node, "symbol", ")")
                self._process(while_statement_node, "symbol", "{")
                self.parse_statements(while_statement_node)
                self._process(while_statement_node, "symbol", "}")
            elif self.tokenizer.peek(0)["value"] == "do":
                do_statement_node = ParseTreeNode("doStatement", None)
                statements_node.add_child(do_statement_node)
                self._process(do_statement_node, "keyword", "do")
                self.parse_subroutine_call(do_statement_node)
                self._process(do_statement_node, "symbol", ";")
            elif self.tokenizer.peek(0)["value"] == "return":
                return_statement_node = ParseTreeNode("returnStatement", None)
                statements_node.add_child(return_statement_node)
                self._process(return_statement_node, "keyword", "return")
                if self.tokenizer.peek(0)["value"] != ";":
                    self.parse_expression(return_statement_node)
                self._process(return_statement_node, "symbol", ";")

    # EXPRESSIONS

    def parse_subroutine_call(self, parent_node):
        if self.tokenizer.peek(1)["value"] == "[":
            self._process(parent_node, "identifier")
            self._process(parent_node, "symbol", "[")
            self.parse_expression(parent_node)
            self._process(parent_node, "symbol", "]")
        elif self.tokenizer.peek(1)["value"] == "(":
            self._process(parent_node, "identifier")
            self._process(parent_node, "symbol", "(")
            self.parse_expression_list(parent_node)
            self._process(parent_node, "symbol", ")")
        elif self.tokenizer.peek(1)["value"] == ".":
            self._process(parent_node, "identifier")
            self._process(parent_node, "symbol", ".")
            self._process(parent_node, "identifier")
            self._process(parent_node, "symbol", "(")
            self.parse_expression_list(parent_node)
            self._process(parent_node, "symbol", ")")
    
    def parse_expression_list(self, parent_node):
        expression_list_node = ParseTreeNode("expressionList", None)
        parent_node.add_child(expression_list_node)
        
        if self.tokenizer.peek(0)["value"] != ")":
            self.parse_expression(expression_list_node)
            
            while self.tokenizer.peek(0)["value"] == ",":
                self._process(expression_list_node, "symbol", ",")
                self.parse_expression(expression_list_node)

    def parse_expression(self, parent_node):
        expression_node = ParseTreeNode("expression", None)
        parent_node.add_child(expression_node)
        
        self.parse_term(expression_node)
        
        while self.tokenizer.peek(0)["value"] in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            self._process(expression_node, "symbol", self.tokenizer.peek(0)["value"])
            self.parse_term(expression_node)

    def parse_term(self, parent_node):
        term_node = ParseTreeNode("term", None)
        parent_node.add_child(term_node)
        
        if self.tokenizer.peek(0)["type"] in ("stringConstant", "integerConstant"):
            self._process(term_node, self.tokenizer.peek(0)["type"], self.tokenizer.peek(0)["value"])
        elif self.tokenizer.peek(0)["type"] == "identifier":
            if self.tokenizer.peek(1)["value"] == "[":  
                self._process(term_node, "identifier")
                self._process(term_node, "symbol", "[")
                self.parse_expression(term_node)  
                self._process(term_node, "symbol", "]")
            elif self.tokenizer.peek(1)["value"] == ".":  
                self.parse_subroutine_call(term_node)
            else:  
                self._process(term_node, "identifier")
        elif self.tokenizer.peek(0)["value"] in ("true", "false", "null", "this"):
            self._process(term_node, "keyword", self.tokenizer.peek(0)["value"])
        elif self.tokenizer.peek(0)["value"] == "(":  
            self._process(term_node, "symbol", "(")
            self.parse_expression(term_node)
            self._process(term_node, "symbol", ")")
        elif self.tokenizer.peek(0)["value"] in ("-", "~"):  
            self._process(term_node, "symbol", self.tokenizer.peek(0)["value"])
            self.parse_term(term_node)

    # PRIVATE

    def _process(self, parent_node, expected_symbol_type=None, expected_symbol_values=None):
        token = self.tokenizer.next_token()
        if expected_symbol_type and token["type"] != expected_symbol_type:
            raise SyntaxError(f"Expected {expected_symbol_type}, got {token['type']}")
        if token["type"] != "identifier":
            if expected_symbol_values and not (token["value"] in expected_symbol_values):
                raise SyntaxError(f"Expected {expected_symbol_values}, got {token['value']}")
        
        self._add_token_node(parent_node, token)

    def _add_token_node(self, parent_node, token):
        token_node = ParseTreeNode(token["type"], token["value"])
        parent_node.add_child(token_node)
