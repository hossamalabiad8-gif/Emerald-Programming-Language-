from dataclasses import dataclass
from errors import LexerError

KEYWORDS = {
    "say",
    "ask",
    "if",
    "orif",
    "else",
    "while",
    "true",
    "false",
    "and",
    "or",
    "not",
    "class",
    "his",
    "return",
    "none",
    "for",
    "in",
    "to",
    "redo",
    "skip",
    "stop",
}

ESCAPES = {
    "n": "\n",
    "t": "\t",
    '"': '"',
    "'": "'",
    "\\": "\\",
}

@dataclass(frozen=True)
class Token:
    type: str
    value: object
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token({self.type}, {self.value!r}, "
            f"{self.line}:{self.column})"
        )


class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.at_line_start = True
        self.indent_stack = [0]

    def current(self):
        if self.position >= len(self.source):
            return None

        return self.source[self.position]

    def advance(self):
        char = self.current()

        if char is None:
            return None

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
            self.at_line_start = True
        else:
            self.column += 1

        return char

    def read_escape(self, line, column):
        self.advance()  # علامة \

        char = self.current()

        if char is None or char == "\n":
            raise LexerError(
                f"Unterminated string at {line}:{column}"
            )

        if char not in ESCAPES:
            raise LexerError(
                f"Unknown escape '\\{char}' "
                f"at {self.line}:{self.column}"
            )

        self.advance()

        return ESCAPES[char]

    def tokenize(self):
        tokens = []

        while self.current() is not None:
            if self.at_line_start:
                self.handle_indentation(tokens)

                if self.current() is None:
                    break

            char = self.current()

            if char in " \t":
                self.advance()
                continue

            if char == "\n":
                line = self.line
                column = self.column

                self.advance()

                tokens.append(
                    Token("NEWLINE", None, line, column)
                )
                continue

            line = self.line
            column = self.column

            if char == "!":
                self.advance()

                if self.current() == "=":
                    self.advance()

                    tokens.append(
                        Token(
                            "NOT_EQUALS",
                            "!=",
                            line,
                            column,
                        )
                    )
                    continue

                while (
                    self.current() is not None
                    and self.current() != "\n"
                ):
                    self.advance()

                continue

            if char.isalpha() or char == "_":
                tokens.append(
                    self.read_identifier(line, column)
                )
                continue

            if char.isdigit():
                tokens.append(
                    self.read_number(line, column)
                )
                continue

            if char == '"':
                tokens.append(
                    self.read_string(line, column)
                )
                continue

            if char == "'":
                tokens.append(
                    self.read_character(line, column)
                )
                continue

            if char == "=":
                self.advance()

                if self.current() == "=":
                    self.advance()

                    tokens.append(
                        Token(
                            "EQUALS_EQUALS",
                            "==",
                            line,
                            column,
                        )
                    )
                else:
                    tokens.append(
                        Token(
                            "EQUALS",
                            "=",
                            line,
                            column,
                        )
                    )

                continue

            if char == ">":
                self.advance()

                if self.current() == "=":
                    self.advance()

                    tokens.append(
                        Token(
                            "GREATER_EQUALS",
                            ">=",
                            line,
                            column,
                        )
                    )
                else:
                    tokens.append(
                        Token(
                            "GREATER",
                            ">",
                            line,
                            column,
                        )
                    )

                continue

            if char == "<":
                self.advance()

                if self.current() == "=":
                    self.advance()

                    tokens.append(
                        Token(
                            "LESS_EQUALS",
                            "<=",
                            line,
                            column,
                        )
                    )
                else:
                    tokens.append(
                        Token(
                            "LESS",
                            "<",
                            line,
                            column,
                        )
                    )

                continue

            if char == "+":
                self.advance()
                if self.current() == "+":
                    self.advance()
                    tokens.append(Token("INCREASE","++",line,column))
                else:
                    tokens.append(
                        Token("PLUS", "+", line, column)
                    )
                continue

            if char == "-":
                self.advance()
                if self.current() == "-":
                    self.advance()
                    tokens.append(Token("DECREASE","--",line,column))
                else:
                    tokens.append(
                        Token("MINUS", "-", line, column)
                    )
                continue

            if char == "*":
                self.advance()

                tokens.append(
                    Token("STAR", "*", line, column)
                )
                continue

            if char == "/":
                self.advance()

                tokens.append(
                    Token("SLASH", "/", line, column)
                )
                continue
            
            if char == "%":
                self.advance()

                tokens.append(
                    Token("PERCENT", "%", line, column)
                )
                continue


            if char == "&":
                self.advance()

                tokens.append(
                    Token(
                        "AMPERSAND",
                        "&",
                        line,
                        column,
                    )
                )
                continue

            if char == "(":
                self.advance()

                tokens.append(
                    Token(
                        "LPAREN",
                        "(",
                        line,
                        column,
                    )
                )
                continue

            if char == ")":
                self.advance()

                tokens.append(
                    Token(
                        "RPAREN",
                        ")",
                        line,
                        column,
                    )
                )
                continue
            if char == "[":
                self.advance()
                tokens.append(
                    Token("LBRACKET", "[", line, column)
                )
                continue

            if char == "]":
                self.advance()
                tokens.append(
                    Token("RBRACKET", "]", line, column)
                )
                continue
                
            if char == ",":
                self.advance()

                tokens.append(
                    Token(
                        "COMMA",
                        ",",
                        line,
                        column,
                    )
                )
                continue
            if char == ".":
                self.advance()

                tokens.append(
                    Token(
                        "DOT",
                        ".",
                        line,
                        column,
                    )
                )
                continue
                
            raise LexerError(
                f"Unexpected character '{char}' "
                f"at {line}:{column}"
            )

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()

            tokens.append(
                Token(
                    "DEDENT",
                    None,
                    self.line,
                    self.column,
                )
            )

        tokens.append(
            Token(
                "EOF",
                None,
                self.line,
                self.column,
            )
        )

        return tokens

    def handle_indentation(self, tokens):
        spaces = 0

        while self.current() == " ":
            self.advance()
            spaces += 1

        if self.current() is None:
            return

        if self.current() == "\t":
            raise LexerError(
                f"Tabs are not allowed for indentation "
                f"at {self.line}:1"
            )

        if self.current() == "\n":
            return

        if self.current() == "!":
            return

        self.at_line_start = False

        current_indent = self.indent_stack[-1]

        if spaces > current_indent:
            self.indent_stack.append(spaces)

            tokens.append(
                Token(
                    "INDENT",
                    None,
                    self.line,
                    1,
                )
            )

        elif spaces < current_indent:
            while (
                len(self.indent_stack) > 1
                and spaces < self.indent_stack[-1]
            ):
                self.indent_stack.pop()

                tokens.append(
                    Token(
                        "DEDENT",
                        None,
                        self.line,
                        1,
                    )
                )

            if spaces != self.indent_stack[-1]:
                raise LexerError(
                    f"Invalid indentation "
                    f"at {self.line}:1"
                )

    def read_identifier(self, line, column):
        value = ""

        while self.current() is not None:
            char = self.current()

            if not (char.isalnum() or char == "_"):
                break

            value += self.advance()

        token_type = (
            "KEYWORD"
            if value in KEYWORDS
            else "IDENTIFIER"
        )

        return Token(
            token_type,
            value,
            line,
            column,
        )

    def read_number(self, line, column):
        value = ""

        while self.current() is not None:
            char = self.current()

            if char.isdigit():
                value += self.advance()
            else:
                break

        if self.current() == ".":
            value += self.advance()

            if (
                self.current() is None
                or not self.current().isdigit()
            ):
                raise LexerError(
                    f"Invalid number "
                    f"at {line}:{column}"
                )

            while self.current() is not None:
                char = self.current()

                if char.isdigit():
                    value += self.advance()
                else:
                    break

            return Token(
                "FLOAT",
                value,
                line,
                column,
            )

        return Token(
            "NUMBER",
            value,
            line,
            column,
        )
    def read_string(self, line, column):
        self.advance()

        value = ""

        while self.current() is not None:
            char = self.current()

            if char == '"':
                self.advance()

                return Token(
                    "STRING",
                    value,
                    line,
                    column,
                )

            if char == "\n":
                raise LexerError(
                    f"Unterminated string "
                    f"at {line}:{column}"
                )
            if char == "\\":
                value += self.read_escape(line, column)
                continue

            value += self.advance()

        raise LexerError(
            f"Unterminated string "
            f"at {line}:{column}"
        )

    def read_character(self, line, column):
        self.advance()

        value = ""

        while self.current() is not None:
            char = self.current()

            if char == "'":
                self.advance()

                if len(value) != 1:
                    raise LexerError(
                        f"Character must contain exactly "
                        f"one character at {line}:{column}"
                    )

                return Token(
                    "CHARACTER",
                    value,
                    line,
                    column,
                )

            if char == "\n":
                raise LexerError(
                    f"Unterminated character "
                    f"at {line}:{column}"
                )
            
            if char == "\\":
                value += self.read_escape(line, column)
                continue

            value += self.advance()
            
            

        raise LexerError(
            f"Unterminated character "
            f"at {line}:{column}"
        )