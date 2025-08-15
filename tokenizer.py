import re

# TOKEN TYPES
KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INTEGER_CONSTANT = "integerConstant"
STRING_CONSTANT = "stringConstant"

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
        token = self.peek(0)
        self.cursor += 1
        return token
    
    def peek(self, ahead):
        token = {"type": self._token_type(self.tokens[self.cursor + ahead]), "value": self.tokens[self.cursor + ahead].strip('"')};
        return token

    def _tokens(self, source):
        # Remove comments but preserve strings
        single_line_comments = r'//.*$'
        multi_line_comments = r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
        
        # First, extract all string literals and replace with placeholders
        string_pattern = r'"[^"]*"'
        string_literals = re.findall(string_pattern, source)
        
        # Replace strings with placeholders to protect them during comment removal
        temp_source = source
        for i, string_lit in enumerate(string_literals):
            placeholder = f"__STRING_PLACEHOLDER_{i}__"
            temp_source = temp_source.replace(string_lit, placeholder, 1)
        
        # Remove comments from the source with placeholders
        text_comments_removed = re.sub(single_line_comments + '|' + multi_line_comments, "", temp_source, flags=re.MULTILINE)
        
        # Put strings back
        for i, string_lit in enumerate(string_literals):
            placeholder = f"__STRING_PLACEHOLDER_{i}__"
            text_comments_removed = text_comments_removed.replace(placeholder, string_lit)
        
        # Now tokenize with proper string handling
        tokens = []
        current_pos = 0
        
        while current_pos < len(text_comments_removed):
            # Skip whitespace
            while current_pos < len(text_comments_removed) and text_comments_removed[current_pos].isspace():
                current_pos += 1
            
            if current_pos >= len(text_comments_removed):
                break
                
            # Check for string literal
            if text_comments_removed[current_pos] == '"':
                # Find the closing quote
                end_pos = current_pos + 1
                while end_pos < len(text_comments_removed) and text_comments_removed[end_pos] != '"':
                    end_pos += 1
                if end_pos < len(text_comments_removed):
                    tokens.append(text_comments_removed[current_pos:end_pos + 1])
                    current_pos = end_pos + 1
                else:
                    raise SyntaxError("Unterminated string literal")
            
            # Check for symbols
            elif text_comments_removed[current_pos] in SYMBOLS:
                tokens.append(text_comments_removed[current_pos])
                current_pos += 1
            
            # Otherwise it's a keyword, identifier, or integer constant
            else:
                end_pos = current_pos
                while (end_pos < len(text_comments_removed) and 
                       not text_comments_removed[end_pos].isspace() and 
                       text_comments_removed[end_pos] not in SYMBOLS and
                       text_comments_removed[end_pos] != '"'):
                    end_pos += 1
                tokens.append(text_comments_removed[current_pos:end_pos])
                current_pos = end_pos

        return tokens

    def _token_type(self, string):
        if (string in KEYWORDS): 
            return KEYWORD
        elif (string in SYMBOLS):
            return SYMBOL
        elif (string.startswith('"') and string.endswith('"')):
            return STRING_CONSTANT
        elif (string[0].isnumeric()):
            return INTEGER_CONSTANT
        elif (string[0] != ""):
            return IDENTIFIER


