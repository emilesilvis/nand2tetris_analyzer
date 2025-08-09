class SymbolTable:
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.indices = {"static":0, "this":0, "argument":0, "local":0}

    def new_class(self):
        self.class_symbols.clear()
        self.indices["static"] = 0
        self.indices["this"] = 0

    def new_subroutine(self):
        self.subroutine_symbols.clear()
        self.indices["argument"] = 0
        self.indices["local"] = 0

    def add(self, name, type, kind):
        jack_kind_to_vm_kind_map = {
            "field": "this",
            "var": "local", 
            "arg": "argument",
            "static": "static"
        }

        vm_kind = jack_kind_to_vm_kind_map.get(kind)

        count = self.indices[vm_kind]
        self.indices[vm_kind] = count + 1

        entry = (type, vm_kind, count)

        if vm_kind in ("static", "this"):
            self.class_symbols[name] = entry
        else:
            self.subroutine_symbols[name] = entry

    def find(self, name):
        pass