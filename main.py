import sys

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import *

sys.setrecursionlimit(3000)

def main():
    if len(sys.argv) != 2:
        print("Emerald: please provide an .em file.")
        return

    filename = sys.argv[1]

    if not filename.endswith(".em"):
        print("Emerald Error: file must end with .em")
        return

    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            source = file.read()

        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        Interpreter().run(program)

    except FileNotFoundError:
        print(f"Emerald Error: file not found: {filename}")

    except (LexerError, ParserError) as error:
        print(f"Emerald Syntax Error: {error}")

    except EmeraldRuntimeError as error:
        if error.line is not None:
            print(f"Emerald Runtime Error at line {error.line}: {error}")
        else:
            print(f"Emerald Runtime Error: {error}")
    
    except RecursionError:
        print(
            "Emerald Runtime Error: too many nested calls "
            "(a function may be calling itself forever)"
        )

    except EOFError:
        print("Emerald Runtime Error: no more input is available")

    except KeyboardInterrupt:
        print("\nEmerald: program stopped.")


if __name__ == "__main__":
    main()