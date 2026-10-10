class EmeraldError(Exception):
    pass


class LexerError(EmeraldError):
    pass


class ParserError(EmeraldError):
    pass


class EmeraldRuntimeError(EmeraldError):
    def __init__(self, message, line=None):
        super().__init__(message)
        self.line = line