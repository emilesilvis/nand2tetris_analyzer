from vm_code_generator import VMCodeGenerator

class CompilationEngine:
    def __init__(self, parse_tree, symbol_table):
        self.parse_tree = parse_tree
        self.symbol_table = symbol_table
        self.vm_code_generator = VMCodeGenerator()
    
    def comile_class(self):
        class_name = [child.value for child in self.parse_tree.children if child.type == "identifier"][0]

        for child in self.parse_tree.children:
            if child.type == "classVarDec":
                self.compile_class_var_dec(child)
            if child.type == "subroutineDec":
                self.compile_subroutine(child, class_name)
            
        return "\n".join(self.vm_code_generator.vm_code)
    
    def compile_class_var_dec(self, node):
        pass

    def compile_subroutine(self, node, class_name):
        # node.debug_dump()
        
        identifiers = [child.value for child in node.children if child.type == "identifier"]

        current_subroutine = self.symbol_table.current_subroutine
        if current_subroutine and current_subroutine in self.symbol_table.subroutine_symbols:
            local_count = self.symbol_table.subroutine_symbols[current_subroutine]["indices"]["local"]
        else:
            local_count = 0

        # print(f"function {class_name}.{identifiers[0]} {local_count}")
        self.vm_code_generator.write_function(class_name, identifiers[0], local_count)

        for child in node.children:
            if child.type == "parameterList":
                self.compile_parameter_list(child)
            if child.type == "subroutineBody":
                self.compile_subroutine_body(child)
    
    def compile_parameter_list(self, node):
        # node.debug_dump()
        pass

    def compile_subroutine_body(self, node):
        # node.debug_dump()
        for child in node.children:
            if child.type == "varDec":
                self.compile_variable_declaration(child)
            if child.type == "statements":
                self.compile_statements(child)

    def compile_variable_declaration(self, node):
        # node.debug_dump()
        pass

    def compile_statements(self, node):
        # node.debug_dump()
        for child in node.children:
            if child.type == "letStatement":
                self.compile_let_statement(child)
            if child.type == "ifStatement":
                self.compile_if_statement(child)
            if child.type == "whileStatement":
                self.compile_while_statement(child)
            if child.type == "doStatement":
                self.compile_do_statement(child)
            if child.type == "returnStatement":
                self.compile_return_statement(child)
    
    def compile_let_statement(self, node):
        # node.debug_dump()
        for child in node.children:
            if child.type == "expression":
                self.compile_expression(child)

    def compile_if_statement(self, node):
        # node.debug_dump()
        pass


    def compile_while_statement(self, node):
        # node.debug_dump()
        pass

    def compile_do_statement(self, node):
        # [object.]method(expressionList)

        # TODO: Should some of this logic not move to comple_expression? 
        expression_list = None
        for child in node.children:
            if child.type == "expressionList":
                expression_list = child
                break

        # Compile expression list (arguments)
        if expression_list:
            n_args = self.compile_expression_list(expression_list)
        else:
            n_args = 0

        # Generate call
        identifiers = [child.value for child in node.children if child.type == "identifier"]

        # Object.method()
        if len(identifiers) == 2:
            object_name, method_name = identifiers
            self.vm_code_generator.write_call(f"{object_name}.{method_name}", n_args)
        # function()
        elif len(identifiers) == 1:
            method_name = identifiers[0]
            self.vm_code_generator.write_call(method_name, n_args)

        self.vm_code_generator.write_pop("temp", "0")

    def compile_return_statement(self, node):
        # return expression or return
        # node.debug_dump()

        # return;
        if len(node.children) == 2:
            self.vm_code_generator.write_push("constant", 0)
            self.vm_code_generator.write_return()
            
        # return exression;
        else:
            pass

    def compile_expression(self, node):
        # print(node)

        # if exp is term:
        #   compileTerm(term)
        # if exp is "term1 op1 term2 op2
        #   term3 op3 ... termn ":
        #   compileTerm(term1)
        #   compileTerm(term2)
        #   output "op1"
        #   compileTerm(term3)
        #   output "op2"
        #   ...
        #   compileTerm(termn)
        #   output "opn–1"

        if node.children[0].value == "do":
            self.compile_term(node)
        else:
            terms = [child for child in node.children if child.type == "term"]
            operations = [child.value for child in node.children if child.type == "symbol"]

            self.compile_term(terms[0])
            for i, operation in enumerate(operations):
                self.compile_term(terms[i + 1])
                if operation == "*":
                    self.vm_code_generator.write_call("Math.multiply", 2)
                elif operation == "/":
                    self.vm_code_generator.write_call("Math.divide", 2)
                else:
                    self.vm_code_generator.write_operation(operation)

    def compile_term(self, node):
        # node.debug_dump()

        for index, child in enumerate(node.children):
            # if term is a constant c:
                # output "push c"
            if child.type == "integerConstant":
                self.vm_code_generator.write_push("constant", child.value)
            
            # if term is "(exp)":
                # compileExpression(exp)
            elif child.type == "expression":
                self.compile_expression(child)
            
            # TODO: Implement this pattern
            # if term is "f (exp1, exp2, ...)":
                # compileExpression(exp1)
                # compileExpression(exp2)
                # ...
                # compileExpression(expn)
                # output "call f n”

        # if term is a variable var:
            # output "push var"
        # if term is "unaryOp term":
            # compileTerm(term)
            # output "unaryOp"


    def compile_expression_list(self, node):
        # node.debug_dump()
        expressions = [child for child in node.children if child.type == "expression"]
        for expression in expressions:
            self.compile_expression(expression)
        
        return len(expressions)