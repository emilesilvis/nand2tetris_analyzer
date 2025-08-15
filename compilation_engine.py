from vm_code_generator import VMCodeGenerator

class CompilationEngine:
    def __init__(self, parse_tree, symbol_table):
        self.parse_tree = parse_tree
        self.symbol_table = symbol_table
        self.vm_code_generator = VMCodeGenerator()
        self.label_count = 0
        self.class_name = None
    
    def compile_class(self):
        self.class_name = [child.value for child in self.parse_tree.children if child.type == "identifier"][0]

        for child in self.parse_tree.children:
            if child.type == "classVarDec":
                self.compile_class_var_dec(child)
            if child.type == "subroutineDec":
                self.compile_subroutine(child)
            
        return "\n".join(self.vm_code_generator.vm_code)
    
    def compile_class_var_dec(self, node):
        pass #Symbol table is already built by the parser

    def compile_subroutine(self, node):
        # node.debug_dump()
        keywords = [child.value for child in node.children if child.type == "keyword"]
        subroutine_type = keywords[0] 

        identifiers = [child.value for child in node.children if child.type == "identifier"]
        
        # For void functions/methods: only one identifier (the subroutine name)
        # For constructors and typed functions: two identifiers (return type, then subroutine name)
        if len(identifiers) == 1:
            subroutine_name = identifiers[0]
        else:
            subroutine_name = identifiers[1]

        self.symbol_table.current_subroutine = subroutine_name

        if subroutine_name in self.symbol_table.subroutine_symbols:
            local_count = self.symbol_table.subroutine_symbols[subroutine_name]["indices"]["local"]
        else:
            local_count = 0

        self.vm_code_generator.write_function(self.class_name, subroutine_name, local_count)

        if subroutine_type == "method":
            self.vm_code_generator.write_push("argument", 0)
            self.vm_code_generator.write_pop("pointer", 0)

        elif subroutine_type == "constructor":
            field_count = self.symbol_table.class_indices["this"]
            self.vm_code_generator.write_push("constant", field_count)
            self.vm_code_generator.write_call("Memory.alloc", 1)
            self.vm_code_generator.write_pop("pointer", 0) # Memory.alloc pushed base address to stack, so we pop it to pointer 0, so this can reflect it
        
        for child in node.children:
            if child.type == "parameterList":
                self.compile_parameter_list(child)
            if child.type == "subroutineBody":
                self.compile_subroutine_body(child)
    
    def compile_parameter_list(self, node):
        pass #Symbol table is already built by the parser

    def compile_subroutine_body(self, node):
        # node.debug_dump()
        for child in node.children:
            if child.type == "varDec":
                self.compile_subroutine_variable_declaration(child)
            if child.type == "statements":
                self.compile_statements(child)

    def compile_subroutine_variable_declaration(self, node):
        pass #Symbol table is already built by the parser

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
        array_index_expression = None
        value_expression = None
        is_array_assignment = False

        # Check if it's array assignment by looking for '[' symbol
        for child in node.children:
            if child.type == "symbol" and child.value == "[":
                is_array_assignment = True
                break
        
        if is_array_assignment:
            # Array assignment: let a[i] = value
            expressions = []
            for child in node.children:
                if child.type == "identifier":
                    var_name = child.value
                elif child.type == "expression":
                    expressions.append(child)

            array_index_expression = expressions[0]
            value_expression = expressions[1]

            symbol_info = self.symbol_table.find(var_name)
            var_type, vm_segment, vm_index = symbol_info

            # Push array index
            self.compile_expression(array_index_expression)

            # Push array base address
            self.vm_code_generator.write_push(vm_segment, vm_index)

            # Calculate element address
            self.vm_code_generator.write_operation("+")

            # Compile value expression
            self.compile_expression(value_expression)
    
            # Store value temporarily
            self.vm_code_generator.write_pop("temp", 0)

            # Set that pointer to element address
            self.vm_code_generator.write_pop("pointer", 1)

            # Get value back and store in array element
            self.vm_code_generator.write_push("temp", 0)
            self.vm_code_generator.write_pop("that", 0)

        else:   
            # Regular assignment: let var = value
            for child in node.children:
                if child.type == "identifier":
                    var_name = child.value
                if child.type == "expression":
                    self.compile_expression(child)

            symbol_info = self.symbol_table.find(var_name)
            if symbol_info:
                var_type, vm_segment, vm_index = symbol_info
                self.vm_code_generator.write_pop(vm_segment, vm_index) # Compile(expressions) pushed results onto the stack, this pops it into wherever the object nedes it

    def compile_if_statement(self, node):
        # node.debug_dump()

        # get expression
        expression = [child for child in node.children if child.type == "expression"][0]

        # get true and false statements
        true_statements = []
        false_statements = []
        else_reached = False

        end_label = f"{self.class_name}_{self.label_count}"
        self.label_count += 1
        false_label = f"{self.class_name}_{self.label_count}"
        self.label_count += 1

        for child in node.children:
            if child.type == "keyword" and child.value == "else":
                else_reached = True
            
            if child.type == "statements":
                if else_reached:
                    false_statements = child
                else:
                    true_statements = child
        
        # compile expression
        self.compile_expression(expression)

        # negate
        self.vm_code_generator.write_operation("not")

        # if-goto FALSE
        self.vm_code_generator.write_if(false_label)

        if true_statements:
            self.compile_statements(true_statements)

        # goto END
        self.vm_code_generator.write_goto(end_label)

        # label FALSE
        self.vm_code_generator.write_label(false_label)

        if false_statements:
            self.compile_statements(false_statements)

        # label END
        self.vm_code_generator.write_label(end_label)

    def compile_while_statement(self, node):
        # node.debug_dump()
        
        # get expression
        expression = [child for child in node.children if child.type == "expression"][0]

        # get white statements
        while_statements = [child for child in node.children if child.type == "statements"][0]

        # label TRUE
        true_label = f"{self.class_name}_{self.label_count}"
        self.label_count += 1
        self.vm_code_generator.write_label(true_label)

        # compile expression
        self.compile_expression(expression)

        # negate
        self.vm_code_generator.write_operation("not")

        # if-goto FALSE
        false_label = f"{self.class_name}_{self.label_count}"
        self.label_count += 1
        self.vm_code_generator.write_if(false_label)

        # compile statements
        self.compile_statements(while_statements)

        # goto TRUE
        self.vm_code_generator.write_goto(true_label)

        # label FALSE
        self.vm_code_generator.write_label(false_label)

    def compile_do_statement(self, node):
        # [object.]method(expressionList)

        expression_list = None
        for child in node.children:
            if child.type == "expressionList":
                expression_list = child
                break
        
        # Generate call
        identifiers = [child.value for child in node.children if child.type == "identifier"]

        # Object.method()
        if len(identifiers) == 2:
            object_name, method_name = identifiers

            symbol_info = self.symbol_table.find(object_name)
            # object instance
            if symbol_info:
                var_type, vm_segment, vm_index = symbol_info
                # Push object reference first
                self.vm_code_generator.write_push(vm_segment, vm_index)
                # Then compile arguments
                if expression_list:
                    n_args = self.compile_expression_list(expression_list)
                else:
                    n_args = 0
                n_args += 1 # Add 1 for 'this' argument
                self.vm_code_generator.write_call(f"{var_type}.{method_name}", n_args)
            # class name
            else:
                # Compile arguments
                if expression_list:
                    n_args = self.compile_expression_list(expression_list)
                else:
                    n_args = 0
                self.vm_code_generator.write_call(f"{object_name}.{method_name}", n_args)
        
        # function()
        elif len(identifiers) == 1:
            method_name = identifiers[0]

            # Check if method call on 'this' object
            if method_name in self.symbol_table.subroutine_symbols:
                # Push 'this' pointer first
                self.vm_code_generator.write_push("pointer", 0)
                # Then compile arguments
                if expression_list:
                    n_args = self.compile_expression_list(expression_list)
                else:
                    n_args = 0
                n_args += 1
                self.vm_code_generator.write_call(f"{self.class_name}.{method_name}", n_args)
            else:
            # Function call
                if expression_list:
                    n_args = self.compile_expression_list(expression_list)
                else:
                    n_args = 0
                self.vm_code_generator.write_call(method_name, n_args)

        self.vm_code_generator.write_pop("temp", 0)

    def compile_return_statement(self, node):
        # return expression or return
        # node.debug_dump()

        # return;
        if len(node.children) == 2:
            self.vm_code_generator.write_push("constant", 0)
            self.vm_code_generator.write_return()
            
        # return exression;
        else:
            # get expression
            expression = [child for child in node.children if child.type == "expression"][0]
            
            self.compile_expression(expression)

            self.vm_code_generator.write_return()

    def compile_expression(self, node):
        # node.debug_dump()

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
            
            elif child.type == "stringConstant":
                string = child.value
                self.vm_code_generator.write_push("constant", len(string))
                self.vm_code_generator.write_call("String.new", 1)
                for char in string:
                    ascii_value = ord(char)
                    self.vm_code_generator.write_push("constant", ascii_value)
                    self.vm_code_generator.write_call("String.appendChar", 2)

            elif child.type == "keyword":
                if child.value == "true":
                    self.vm_code_generator.write_push("constant", 1)
                    self.vm_code_generator.write_operation("neg")  # true is -1
                elif child.value == "false":
                    self.vm_code_generator.write_push("constant", 0)
                elif child.value == "null":
                    self.vm_code_generator.write_push("constant", 0)
                elif child.value == "this":
                    self.vm_code_generator.write_push("pointer", 0)
            
            # if term is "(exp)":
                # compileExpression(exp)
            elif child.type == "expression":
                self.compile_expression(child)
            
            # if term is "f (exp1, exp2, ...)":
                # compileExpression(exp1)
                # compileExpression(exp2)
                # ...
                # compileExpression(expn)
                # output "call f n”
            elif len(node.children) > 2 and node.children[0].type == "identifier" and node.children[1].value == ".":
                object_name = node.children[0].value
                method_name = node.children[2].value
                expression_list = node.children[4]
                
                # Check if it's a method call on 'this' (current object)
                if object_name == "this":
                    # Push 'this' pointer first
                    self.vm_code_generator.write_push("pointer", 0)
                    n_args = self.compile_expression_list(expression_list)
                    n_args += 1  # Add 1 for 'this' argument
                    self.vm_code_generator.write_call(f"{self.class_name}.{method_name}", n_args)
                else:
                    # Check if object_name is a variable (object instance)
                    symbol_info = self.symbol_table.find(object_name)
                    if symbol_info:
                        var_type, vm_segment, vm_index = symbol_info
                        self.vm_code_generator.write_push(vm_segment, vm_index)
                        n_args = self.compile_expression_list(expression_list)
                        n_args += 1
                        self.vm_code_generator.write_call(f"{var_type}.{method_name}", n_args)
                    else:
                        # Class function call
                        n_args = self.compile_expression_list(expression_list)
                        self.vm_code_generator.write_call(f"{object_name}.{method_name}", n_args)
                break
        
            # Array access: identifier[expression]
            elif (index + 2 < len(node.children) and child.type == "identifier" and index + 1 < len(node.children) and node.children[index + 1].value == "["):
                array_name = child.value
                array_index_expression = node.children[index + 2]

                # Push array index
                self.compile_expression(array_index_expression)

                # Push array base address
                symbol_info = self.symbol_table.find(array_name)
                var_type, vm_segment, vm_index = symbol_info
                self.vm_code_generator.write_push(vm_segment, vm_index)

                # Calculate element address and access
                self.vm_code_generator.write_operation("+")
                self.vm_code_generator.write_pop("pointer", 1) # Set that pointer
                self.vm_code_generator.write_push("that", 0) # Get array element
                break

            # if term is a variable var:
                            # output "push var"
            elif child.type == "identifier":
                var_name = child.value

                symbol_info = self.symbol_table.find(var_name)
                if symbol_info:
                    var_type, vm_segment, vm_index = symbol_info
                    self.vm_code_generator.write_push(vm_segment, vm_index)
                else:
                    raise Exception(f"Undefined variable: {var_name}")

            # if term is "unaryOp term":
                # compileTerm(term)
                # output "unaryOp"
            elif child.type == "symbol" and child.value in ["-", "~"]:
                term = node.children[index + 1]
                self.compile_term(term)
                if child.value == "-":
                    self.vm_code_generator.write_operation("neg")
                elif child.value == "~":
                    self.vm_code_generator.write_operation("not")

    def compile_expression_list(self, node):
        # node.debug_dump()
        expressions = [child for child in node.children if child.type == "expression"]
        for expression in expressions:
            self.compile_expression(expression)
        
        return len(expressions)