class VMCodeGenerator:
    JACK_TO_VM_OPS = {
        "+": "add",
        "-": "sub",
        "&": "and",
        "|": "or",
        "<": "lt",
        ">": "gt",
        "=": "eq",
        "neg": "neg",
        "not": "not"
    }

    def __init__(self):
        self.vm_code = []

    def write_push(self, segment, index):
        self.vm_code.append(
            f"    push {segment} {index}"
        )

    def write_pop(self, segment, index):
        self.vm_code.append(
            f"    pop {segment} {index}"
        )

    def write_operation(self, operation):
        self.vm_code.append("    " + self.JACK_TO_VM_OPS[operation])

    def write_label(self, label):
        self.vm_code.append(
            f"label {label}"
        )

    def write_goto(self, label):
        self.vm_code.append(
            f"    goto {label}"
        )

    def write_if(self, label):
        self.vm_code.append(
            f"    if-goto {label}"
        )

    def write_call(self, name, n_args):
        self.vm_code.append(
            f"    call {name} {n_args}"
        )

    def write_function(self, class_name, function_name, n_vars):
        self.vm_code.append(
            f"function {class_name}.{function_name} {n_vars}"
        )
    
    def write_return(self):
        self.vm_code.append("    return")