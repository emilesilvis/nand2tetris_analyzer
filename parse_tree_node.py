class ParseTreeNode():
    def __init__(self, type, value):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)
    
    def debug_dump(self, indent=0):
        print
        indent_str = "  " * indent
        output = f"{indent_str}{self.type}"
        if self.value is not None:
            output += f": {self.value}"
        print(output)
        
        for child in self.children:
            child.debug_dump(indent + 1)

        if indent == 0:
            print("=========")
        