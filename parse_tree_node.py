class ParseTreeNode():
    def __init__(self, type, value):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)