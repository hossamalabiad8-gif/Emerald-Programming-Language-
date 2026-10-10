from emerald_ast import *
from errors import ParserError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.in_class= False
    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()

        if token.type != "EOF":
            self.position += 1

        return token

    def check(self, token_type, value=None):
        token = self.current()

        if token.type != token_type:
            return False

        if value is not None and token.value != value:
            return False

        return True

    def expect(self, token_type, value=None):  
        token = self.current()  

        if not self.check(token_type, value):  
            expected = value or token_type  

            raise ParserError(  
                f"Expected {expected} "  
                f"at {token.line}:{token.column}"  
            )  

        return self.advance()  

    def skip_newlines(self):
        while self.check("NEWLINE"):
            self.advance()

    def parse(self):
        statements = []

        self.skip_newlines()

        while not self.check("EOF"):
            statements.append(
                self.parse_statement()
            )

            self.skip_newlines()

        return Program(statements)

    def parse_statement(self):
        line = self.current().line
        statement = self.parse_statement_inner()
        statement.line = line
        return statement

    def parse_statement_inner(self):
        if self.check("KEYWORD", "say"):
            return self.parse_say()
            
        if self.check("KEYWORD", "return"):
            return self.parse_return()
    
        if self.check("KEYWORD", "ask"):
            return self.parse_ask()
            
        if self.check("KEYWORD", "if"):
            return self.parse_if()

        if self.check("KEYWORD", "while"):
            return self.parse_while()
            
        if self.check("KEYWORD", "for"):
            return self.parse_for()
            
        if self.check("KEYWORD", "class"):
            return self.parse_class()

        if self.check("KEYWORD","redo"):
            return self.parse_redo()

        if self.check("KEYWORD", "skip"):
            self.expect("KEYWORD", "skip")
            self.end_simple_statement()
            return SkipStatement()

        if self.check("KEYWORD", "stop"):
            self.expect("KEYWORD", "stop")
            self.end_simple_statement()
            return StopStatement()
        
        
        if (
            self.check("IDENTIFIER")
            or self.check("KEYWORD", "his")
        ):
            return self.parse_expression_statement()
        token = self.current()

        raise ParserError(
            f"Unexpected token '{token.value}' "
            f"at {token.line}:{token.column}"
        )

    
    def parse_unary(self):
        if self.check("MINUS"):
            self.advance()

            operand = self.parse_unary()

            if (
                isinstance(operand, Literal)
                and isinstance(operand.value, (int, float))
                and not isinstance(operand.value, bool)
            ):
                return Literal(-operand.value)

            return BinaryExpression(
                Literal(-1),
                "*",
                operand,
            )

        return self.parse_primary()
    
    
    def begin_block(self):
        self.expect("NEWLINE")
        self.skip_newlines()
        self.expect("INDENT")

    def at_statement_end(self):
        return (
            self.check("NEWLINE")
            or self.check("DEDENT")
            or self.check("EOF")
        )

    def parse_arguments(self):
        self.expect("LPAREN")

        arguments = []

        if not self.check("RPAREN"):
            while True:
                arguments.append(
                    self.parse_value()
                )

                if not self.check("COMMA"):
                    break

                self.advance()

        self.expect("RPAREN")

        return arguments

    
    def parse_say(self):
        self.expect("KEYWORD", "say")

        return SayStatement([self.parse_value()])
        
    def parse_return(self):
        self.expect("KEYWORD", "return")

        if (
            self.check("NEWLINE")
            or self.check("DEDENT")
            or self.check("EOF")
        ):
            return ReturnStatement(Literal(None))

        return ReturnStatement(self.parse_value())
    def parse_ask(self):
        self.expect("KEYWORD", "ask")

        prompt = self.parse_value()

        variable = self.expect("IDENTIFIER")

        return AskStatement(
            prompt,
            variable.value,
        )
    def parse_ask_expression(self):
        self.expect("KEYWORD", "ask")

        prompt = self.parse_value()

        input_type = None

        if self.check("IDENTIFIER"):
            input_type = self.advance().value

        return AskExpression(
            prompt,
            input_type,
        )
        
    def parse_if(self):
        self.expect("KEYWORD", "if")

        condition = self.parse_value()

        self.expect("NEWLINE")
        self.skip_newlines()
        self.expect("INDENT")

        body = []

        self.skip_newlines()

        while not self.check("DEDENT"):
            if self.check("EOF"):
                raise ParserError(
                    "Expected end of if block."
                )

            body.append(
                self.parse_statement()
            )

            self.skip_newlines()

        self.expect("DEDENT")

        orif_branches = []

        while self.check("KEYWORD", "orif"):
            self.advance()

            orif_condition = self.parse_value()

            self.expect("NEWLINE")
            self.skip_newlines()
            self.expect("INDENT")

            orif_body = []

            self.skip_newlines()

            while not self.check("DEDENT"):
                if self.check("EOF"):
                    raise ParserError(
                        "Expected end of orif block."
                    )

                orif_body.append(
                    self.parse_statement()
                )
    
                self.skip_newlines()

            self.expect("DEDENT")

            orif_branches.append(
                (orif_condition, orif_body)
            )

        else_body = []

        if self.check("KEYWORD", "else"):
            self.advance()

            self.expect("NEWLINE")
            self.skip_newlines()
            self.expect("INDENT")

            self.skip_newlines()

            while not self.check("DEDENT"):
                if self.check("EOF"):
                    raise ParserError(
                        "Expected end of else block."
                    )

                else_body.append(
                    self.parse_statement()
                )

                self.skip_newlines()
    
            self.expect("DEDENT")

        return IfStatement(
            condition,
            body,
            orif_branches,
            else_body,
        )

    def parse_while(self):
        self.expect("KEYWORD", "while")

        condition = self.parse_value()

        self.expect("NEWLINE")
        self.skip_newlines()
        self.expect("INDENT")

        body = []

        self.skip_newlines()

        while not self.check("DEDENT"):
            if self.check("EOF"):
                raise ParserError(
                    "Expected end of while block."
                )

            body.append(
                self.parse_statement()
            )

            self.skip_newlines()

        self.expect("DEDENT")

        return WhileStatement(
            condition,
            body,
        )
    def parse_for(self):
        self.expect("KEYWORD", "for")

        variable = self.expect("IDENTIFIER")

        self.expect("KEYWORD", "in")

        start = self.parse_value()

        self.expect("KEYWORD", "to")

        end = self.parse_value()

        self.expect("NEWLINE")
        self.skip_newlines()
        self.expect("INDENT")

        body = []

        self.skip_newlines()

        while not self.check("DEDENT"):
            if self.check("EOF"):
                raise ParserError(
                    "Expected end of for loop."
                )

            body.append(self.parse_statement())
            self.skip_newlines()

        self.expect("DEDENT")

        return ForStatement(
            variable.value,
            start,
            end,
            body,
        )
    
    
    def parse_value(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()

        while self.check("KEYWORD", "or"):
            operator = self.advance()
            right = self.parse_and()

            left = BinaryExpression(
                left,
                operator.value,
                right,
            )

        return left

    def parse_and(self):
        left = self.parse_not()

        while self.check("KEYWORD", "and"):
            operator = self.advance()
            right = self.parse_not()

            left = BinaryExpression(
                left,
                operator.value,
                right,
            )

        return left
    def parse_not(self):
        if self.check("KEYWORD", "not"):
            self.advance()

            operand = self.parse_not()

            return UnaryExpression(
                "not",
                operand,
            )

        return self.parse_comparison()
    def parse_comparison(self):
        left = self.parse_concat()

        comparison_types = (
            "EQUALS_EQUALS",
            "NOT_EQUALS",
            "GREATER",
            "LESS",
            "GREATER_EQUALS",
            "LESS_EQUALS",
        )

        if self.current().type in comparison_types:
            operator = self.advance()
            right = self.parse_concat()

            return ComparisonExpression(
                left,
                operator.value,
                right,
            )

        return left

    def parse_concat(self):
        left = self.parse_term()

        if not self.check("AMPERSAND"):
            return left

        parts = [left]

        while self.check("AMPERSAND"):
            self.advance()
            parts.append(self.parse_term())

        return ConcatExpression(parts)

    def parse_term(self):
        left = self.parse_factor()

        while (
            self.check("PLUS")
            or self.check("MINUS")
        ):
            operator = self.advance()
            right = self.parse_factor()

            left = BinaryExpression(
                left,
                operator.value,
                right,
            )

        return left

    def parse_factor(self):
        left = self.parse_unary()

        while (
            self.check("STAR")
            or self.check("SLASH")
            or self.check("PERCENT")
        ):
            operator = self.advance()
            right = self.parse_unary()

            left = BinaryExpression(
                left,
                operator.value,
                right,
            )

        return left
    def end_simple_statement(self):
        if self.check("NEWLINE"):
            self.advance()
            return

        if self.check("DEDENT") or self.check("EOF"):
            return

        token = self.current()
        raise ParserError(
            f"Unexpected '{token.value}' "
            f"at {token.line}:{token.column}"
        )
    def parse_primary(self):
        token = self.current()

        if token.type == "LPAREN":
            self.advance()

            value = self.parse_value()

            self.expect("RPAREN")

            return value
        if token.type == "LBRACKET":
            self.advance()

            elements = []

            if not self.check("RBRACKET"):
                elements.append(self.parse_value())

                while self.check("COMMA"):
                    self.advance()
                    elements.append(self.parse_value())

            self.expect("RBRACKET")

            return ListLiteral(elements)
        if token.type == "STRING":
            self.advance()
            return Literal(token.value)

        if token.type == "CHARACTER":
            self.advance()
            return Literal(token.value)

        if token.type == "NUMBER":
            self.advance()
            return Literal(int(token.value))

        if token.type == "FLOAT":
            self.advance()
            return Literal(float(token.value))
        if (
            token.type == "KEYWORD"
            and token.value == "ask"
        ):
            return self.parse_ask_expression()
            
        if (
            token.type == "KEYWORD"
            and token.value == "true"
        ):
            self.advance()
            return Literal(True)

        if (
            token.type == "KEYWORD"
            and token.value == "false"
        ):
            self.advance()
            return Literal(False)

        if (
            token.type == "KEYWORD"
            and token.value == "none"
        ):
            self.advance()
            return Literal(None)

        if (
            token.type == "IDENTIFIER"
            or (
                token.type == "KEYWORD"
                and token.value == "his"
            )
        ):
            self.advance()

            node = Identifier(token.value)

            if self.check("LPAREN"):
                node = self.parse_call_expression(token)

            while (
                self.check("DOT")
                or self.check("LBRACKET")
            ):
                if self.check("LBRACKET"):
                    self.advance()

                    index = self.parse_value()

                    self.expect("RBRACKET")

                    node = IndexAccess(
                        node,
                        index,
                    )

                else:
                    self.advance()

                    property_name = self.expect(
                        "IDENTIFIER"
                    )

                    if self.check("LPAREN"):
                        arguments = self.parse_arguments()

                        node = MethodCall(
                            node,
                            property_name.value,
                            arguments,
                        )

                    else:
                        node = PropertyAccess(
                            node,
                            property_name.value,
                        )

            return node

        raise ParserError(
            f"Expected a value "
            f"at {token.line}:{token.column}"
        )

    def parse_call_expression(self, name):
        self.expect("LPAREN")

        arguments = []

        if not self.check("RPAREN"):
            while True:
                arguments.append(
                    self.parse_value()
                )

                if not self.check("COMMA"):
                    break

                self.advance()

        self.expect("RPAREN")

        return FunctionCall(
            name.value,
            arguments,
        )

    def parse_class(self):
        self.expect("KEYWORD", "class")

        name = self.expect("IDENTIFIER")

        parent = None

        if self.check("IDENTIFIER"):
            parent = self.advance().value

        if not self.check("EOF"):
            self.expect("NEWLINE")

        self.skip_newlines()

        if not self.check("INDENT"):
            return ClassDeclaration(
                name.value,
                parent,
                [],
            )

        self.expect("INDENT")

        old_in_class = self.in_class
        self.in_class = True

        body = []

        try:
            self.skip_newlines()

            while not self.check("DEDENT"):
                if self.check("EOF"):
                    raise ParserError("Expected end of class.")

                body.append(self.parse_statement())
                self.skip_newlines()

            self.expect("DEDENT")

        finally:
            self.in_class = old_in_class

        return ClassDeclaration(
            name.value,
            parent,
            body,
        )
    def parse_expression_statement(self):
        token = self.current()

        target = self.parse_primary()

        if self.check("EQUALS"):
            self.advance()

            value = self.parse_value()

            if isinstance(target, Identifier):
                if target.name == "his":
                    raise ParserError(
                        f"Cannot assign to 'his' "
                        f"at {token.line}:{token.column}"
                    )

                return VariableDeclaration(
                    target.name,
                    value,
                )

            if isinstance(target, PropertyAccess):
                return PropertyAssignment(
                    target.object,
                    target.property,
                    value,
                )
            
            if isinstance(target, IndexAccess):
                return IndexAssignment(
                target.collection,
                target.index,
                value)
            
            raise ParserError(
                f"Invalid assignment target "
                f"at {token.line}:{token.column}"
            )
        if self.check("INCREASE"):
            self.advance()

            if self.at_statement_end():
                return UpdateExpression(target, "++", None)

            amount = self.parse_value()

            return UpdateExpression(
                target,
                "++",
                amount,
            )


        elif self.check("DECREASE"):
            self.advance()

            if self.at_statement_end():
                return UpdateExpression(target, "--", None)

            amount = self.parse_value()

            return UpdateExpression(
                target,
                "--",
                amount,
            )
        if isinstance(target, FunctionCall):
            if self.check("NEWLINE"):
                self.skip_newlines()

                if self.check("INDENT"):
                    return self.parse_function_body(
                        target,
                        token,
                    )

            return target

        if isinstance(target, MethodCall):
            return target

        raise ParserError(
            f"Expected '=' or a call "
            f"at {token.line}:{token.column}"
        )

    def parse_function_body(self, call, token):
        parameters = []
        if self.in_class:
            if not call.arguments:
                raise ParserError(
                    f"Method '{call.name}' "
                    f"must have 'his' as its first parameter "
                    f"at {token.line}:{token.column}"
                )

            first = call.arguments[0]

            if (
                not isinstance(first, Identifier)
                or first.name != "his"
            ):
                raise ParserError(
                    f"Method '{call.name}' "
                    f"must have 'his' as its first parameter "
                    f"at {token.line}:{token.column}"
                )
        for argument in call.arguments:
            if not isinstance(argument, Identifier):
                raise ParserError(
                    f"Function parameters must be identifiers "
                    f"at {token.line}:{token.column}"
                )

            parameters.append(argument.name)

        self.expect("INDENT")

        body = []

        self.skip_newlines()

        while not self.check("DEDENT"):
            if self.check("EOF"):
                raise ParserError(
                    "Expected end of function."
                )

            body.append(
                self.parse_statement()
            )

            self.skip_newlines()

        self.expect("DEDENT")

        return FunctionDeclaration(
            call.name,
            parameters,
            body,
        )
    def parse_redo(self):
        self.expect("KEYWORD", "redo")
        if self.check("NUMBER"):
            amount = int(self.current().value)
            self.advance()
        else:
            amount = None
        self.expect("NEWLINE")
        self.skip_newlines()
        self.expect("INDENT")
        body = []
        self.skip_newlines()
        while not self.check("DEDENT"):
            if self.check("EOF"):
                raise ParserError("Expected end of redo block.")
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect("DEDENT")
        return RedoStatement(amount,body)