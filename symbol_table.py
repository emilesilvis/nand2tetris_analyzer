class SymbolTable:
    JACK_TO_VM = {
        "field": "this",
        "var": "local", 
        "arg": "argument",
        "static": "static"
    }

    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.class_indices = {"static":0, "this":0}
        self.current_subroutine = None

    def add_class_symbol(self, name, type, kind):
        vm_kind = self.JACK_TO_VM.get(kind)

        count = self.class_indices[vm_kind]
        self.class_indices[vm_kind] = count + 1

        entry = (type, vm_kind, count)

        self.class_symbols[name] = entry

    def add_subroutine(self, subroutine_name):
        self.current_subroutine = subroutine_name

        self.subroutine_symbols[subroutine_name] = {
            "symbols": {},
            "indices": {"argument":0, "local":0}
        }

    def add_subroutine_symbol(self, name, type, kind):
        vm_kind = self.JACK_TO_VM.get(kind)

        count = self.subroutine_symbols[self.current_subroutine]["indices"][vm_kind]
        self.subroutine_symbols[self.current_subroutine]["indices"][vm_kind] = count + 1

        entry = (type, vm_kind, count)

        self.subroutine_symbols[self.current_subroutine]["symbols"][name] = entry

    def find(self, name):
        pass