import re

# TOKEN TYPES
KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
IDENTIFIER = "IDENTIFIER"
INTEGER_CONSTANT = "INTEGER_CONSTANT"
STRING_CONSTANT = "STRING_CONSTANT"

# Keywords
KEYWORDS = [
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'
]

SYMBOLS = [
    '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
]

class Tokenizer:
    def __init__(self, source):
        self.tokens = self._tokens(source)
        self.cursor = 0

    def next_token(self):
        token = {"token_type": self._token_type(self.tokens[self.cursor]), "token_value": self.tokens[self.cursor]};
        self.cursor += 1
        return token

    def _tokens(self, source):
        single_line_comments = r'//.*$'
        multi_line_comments = r'/\*.*?\*/'
        text_comments_removed = re.sub(single_line_comments + '|' + multi_line_comments, "", source, flags=re.MULTILINE)
        newlines_removed = text_comments_removed.replace('\n', ' ')
        split_pattern = r'([{}()\[\].,;+\-*/&|<>=~])'
        parts = re.split(split_pattern, newlines_removed)
        
        tokens = []
        for part in parts:
            part = part.strip()
            if part:
                if (part[0] == "\"" and part[-1] == "\""):
                    tokens.append(part)
                else:
                    [tokens.append(word) for word in part.split()]

        return tokens

    def _token_type(self, string):
        if (string in KEYWORDS): 
            return KEYWORD
        elif (string in SYMBOLS):
            return SYMBOL
        elif (string[0] == "\"" or string[-1] == "\"" ):
            return STRING_CONSTANT
        elif (string[0].isnumeric()):
            return INTEGER_CONSTANT
        elif (string[0] != ""):
            return IDENTIFIER


