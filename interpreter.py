from emerald_ast import *
from errors import EmeraldRuntimeError
from scope import Scope
import operator

COMPARISONS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}
def format_value(value, nested=False):
    if value is True:
        return "true"

    if value is False:
        return "false"

    if value is None:
        return "nothing"

    if isinstance(value, float):
        return format(value, ".10g")

    if isinstance(value, list):
        items = ", ".join(
            format_value(item, True) for item in value
        )
        return f"[{items}]"

    if isinstance(value, str) and nested:
        return f'"{value}"'

    if isinstance(value, EmeraldObject):
        return f"<{value.class_definition.name} object>"

    return str(value)
class EmeraldObject:
    def __init__(self, class_definition):
        self.class_definition = class_definition
        self.properties = {}

class EmeraldReturn(Exception):
    def __init__(self, value):
        self.value = value

class EmeraldSkip(Exception):
    pass


class EmeraldStop(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.global_scope = Scope()
        self.scope = self.global_scope
        self.functions = {}
        self.classes = {}
        self.current_object = None

    def run(self, program):
        try:
            for statement in program.statements:
                self.execute(statement)

        except EmeraldReturn:
            raise EmeraldRuntimeError(
                "'return' can only be used inside a function"
            )

        except (EmeraldSkip, EmeraldStop):
            raise EmeraldRuntimeError(
                "'skip' and 'stop' can only be used inside a loop"
            )

    def execute(self, statement):
        try:
            self.execute_statement(statement)
        except EmeraldRuntimeError as error:
            if error.line is None:
                error.line = getattr(statement, "line", None)
            raise

    def execute_statement(self, statement):
        if isinstance(statement, FunctionDeclaration):
            self.functions[statement.name] = statement
            return

        if isinstance(statement, ClassDeclaration):
            self.classes[statement.name] = statement
            return

        if isinstance(statement, VariableDeclaration):
            value = self.evaluate(statement.value)
            self.scope.set(statement.name, value)
            return
            
        if isinstance(statement, ReturnStatement):
            value = self.evaluate(statement.value)

            raise EmeraldReturn(value)
            
        if isinstance(statement, PropertyAssignment):
            object_value = self.evaluate(
                statement.object
            )

            if not isinstance(
                object_value,
                EmeraldObject,
            ):
                raise EmeraldRuntimeError(
                    "Property assignment requires an object."
                )

            value = self.evaluate(statement.value)

            object_value.properties[
                statement.property
            ] = value

            return
        if isinstance(statement, IndexAssignment):
            collection = self.evaluate(statement.collection)
            index = self.evaluate(statement.index)

            if not isinstance(collection, list):
                raise EmeraldRuntimeError(
                    "Cannot assign an index on this value. Expected a List."
                )

            if isinstance(index, bool):
                raise EmeraldRuntimeError(
                    "Boolean values cannot be used as List indices."
                )

            if not isinstance(index, int):
                raise EmeraldRuntimeError(
                    "List index must be a whole number."
                )

            if index < 1:
                raise EmeraldRuntimeError(
                    f"List index must be at least 1, got {index}."
                )

            if index > len(collection):
                raise EmeraldRuntimeError(
                    f"List index out of range. Expected an index between 1 and {len(collection)}, got {index}."
                )
            
            value = self.evaluate(statement.value)

            expected = self.type_name(collection[0])
            actual = self.type_name(value)

            if actual != expected:
                raise EmeraldRuntimeError(
                    f"List type mismatch. "
                    f"Expected {expected}, got {actual}."
                )

            collection[index - 1] = value

            return
        if isinstance(statement, FunctionCall):
            self.evaluate(statement)
            return
            
        if isinstance(statement, MethodCall):
            self.evaluate(statement)
            return

        if isinstance(statement, WhileStatement):
            while self.check_condition(
                self.evaluate(statement.condition),
                "'while' condition",
            ):
                try:
                    for child in statement.body:
                        self.execute(child)
                except EmeraldSkip:
                    continue
                except EmeraldStop:
                    break
            return
        if isinstance(statement, ForStatement):
            start = self.evaluate(statement.start)
            end = self.evaluate(statement.end)

            if (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
            ):
                raise EmeraldRuntimeError(
                    "For loop range must use whole numbers"
                )

            old_scope = self.scope
            self.scope = Scope(parent=old_scope)

            try:
                step = 1 if start <= end else -1

                for value in range(start, end + step, step):
                    self.scope.define(statement.variable, value)

                    try:
                        for child in statement.body:
                            self.execute(child)
                    except EmeraldSkip:
                        continue
                    except EmeraldStop:
                        break

            finally:
                self.scope = old_scope

            return
        if isinstance(statement, SayStatement):
            values = [
                self.evaluate(value)
                for value in statement.values
            ]

            print("".join(format_value(value) for value in values))
            return
        if isinstance(statement, AskStatement):
            prompt = self.evaluate(
                statement.prompt
            )

            value = input(prompt)

            self.scope.set(
                statement.variable,
                value,
            )

            return
        if isinstance(statement, IfStatement):
            if self.check_condition(
                self.evaluate(statement.condition),
                "'if' condition",
            ):
                for child in statement.body:
                    self.execute(child)

            else:
                matched = False

                for condition, body in statement.orif_branches:
                    if self.check_condition(
                        self.evaluate(condition),
                        "'orif' condition",
                    ):
                        for child in body:
                            self.execute(child)

                        matched = True
                        break

                if not matched:
                    for child in statement.else_body:
                        self.execute(child)

            return
        if isinstance(statement, UpdateExpression):
            current_value = self.evaluate(statement.variable)

            amount = (
                1
                if statement.amount is None
                else self.evaluate(statement.amount)
            )

            if (
                not isinstance(current_value, (int, float))
                or isinstance(current_value, bool)
            ):
                raise EmeraldRuntimeError(
                    "Update operation requires a number"
                )
        
            if (
                not isinstance(amount, (int, float))
                or isinstance(amount, bool)
            ):
                raise EmeraldRuntimeError(
                    "Update amount must be a number"
                )

            if statement.operation == "++":
                new_value = current_value + amount

            elif statement.operation == "--":
                new_value = current_value - amount

            else:
                raise EmeraldRuntimeError(
                    f"Unknown update operation '{statement.operation}'"
                )

            self.assign_target(statement.variable, new_value)

            return
            
        if isinstance(statement, RedoStatement):
            body = statement.body
            if statement.amount is None:
                while True:
                    try:
                        for t in body:
                            self.execute(t)
                    except EmeraldSkip:
                        continue
                    except EmeraldStop:
                        break
            else:
                value = statement.amount
                for _ in range(value):
                    try:
                        for j in body:
                            self.execute(j)
                    except EmeraldSkip:
                        continue
                    except EmeraldStop:
                        break
            return
        if isinstance(statement, SkipStatement):
            raise EmeraldSkip()


        if isinstance(statement, StopStatement):
            raise EmeraldStop()
            
        raise EmeraldRuntimeError(
            f"Unknown statement: "
            f"{type(statement).__name__}"
        )

    def check_condition(self, value, where):
        if isinstance(value, bool):
            return value

        raise EmeraldRuntimeError(
            f"{where} must be true or false, "
            f"got {self.type_name(value)}. "
            f"Try a comparison like 'x != 0'."
        )

    def type_name(self, value):
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "str"
        if isinstance(value, list):
            return "list"
        if value is None:
            return "null"
        if isinstance(value, EmeraldObject):
            return value.class_definition.name
        return type(value).__name__

    def check_same_type(self, elements):
        if not elements:
            return

        expected = self.type_name(elements[0])

        for position, item in enumerate(elements[1:], start=2):
            actual = self.type_name(item)

            if actual != expected:
                raise EmeraldRuntimeError(
                    f"List items must all be the same type. "
                    f"Expected {expected}, got {actual} "
                    f"at item {position}."
                )

    def assign_target(self, target, value):
        if isinstance(target, Identifier):
            try:
                self.scope.assign(target.name, value)
            except KeyError:
                raise EmeraldRuntimeError(
                    f"Undefined variable '{target.name}'"
                )
            return

        if isinstance(target, PropertyAccess):
            object_value = self.evaluate(target.object)

            if not isinstance(object_value, EmeraldObject):
                raise EmeraldRuntimeError(
                    "Property update requires an object."
                )

            object_value.properties[target.property] = value
            return

        if isinstance(target, IndexAccess):
            collection = self.evaluate(target.collection)
            index = self.evaluate(target.index)
            if self.type_name(value) != self.type_name(collection[index - 1]):
                raise EmeraldRuntimeError(
                    "List type mismatch. "
                    f"Expected {self.type_name(collection[index - 1])}, "
                    f"got {self.type_name(value)}."
                )
            collection[index - 1] = value
            return

        raise EmeraldRuntimeError(
            "Update operation requires a variable, a property, or a list item"
        )

    def call_function(self, call):
        if call.name not in self.functions:
            raise EmeraldRuntimeError(
                f"Undefined function "
                f"'{call.name}'"
            )

        function = self.functions[call.name]

        if len(call.arguments) != len(function.parameters):
            raise EmeraldRuntimeError(
                f"Function '{call.name}' expects "
                f"{len(function.parameters)} arguments"
            )
        arguments = [
            self.evaluate(argument)
            for argument in call.arguments
        ]

        old_scope = self.scope
        self.scope = Scope(parent=self.global_scope)

        for parameter, argument in zip(
            function.parameters,
            arguments,
        ):
            self.scope.define(
                parameter,
                argument,
            )

        try:
            for statement in function.body:
                self.execute(statement)

        except EmeraldReturn as result:
            return result.value
            
        except (EmeraldSkip, EmeraldStop):
            raise EmeraldRuntimeError(
                "'skip' and 'stop' can only be used inside a loop"
            )

        finally:
            self.scope = old_scope

        return None
    def find_method(self, class_definition, name):
        current_class = class_definition

        while current_class is not None:
            for statement in current_class.body:
                if (
                    isinstance(
                        statement,
                        FunctionDeclaration,
                    )
                    and statement.name == name
                ):
                    return statement
    
            if current_class.parent is None:
                break

            if current_class.parent not in self.classes:
                raise EmeraldRuntimeError(
                    f"Undefined parent class "
                    f"'{current_class.parent}'"
                )

            current_class = self.classes[
                current_class.parent
            ]

        return None
        
    def call_method(self, call):
        object_value = self.evaluate(call.object)

        if not isinstance(object_value, EmeraldObject):
            raise EmeraldRuntimeError(
                f"Cannot call method '{call.name}' on this value. "
                f"Expected an object."
            )

        method = self.find_method(
            object_value.class_definition,
            call.name,
        )

        if method is None:
            raise EmeraldRuntimeError(
                f"Undefined method "
                f"'{call.name}'"
            )
    
        if len(call.arguments) != len(method.parameters) - 1:
            raise EmeraldRuntimeError(
                f"Method '{call.name}' expects "
                f"{len(method.parameters) - 1} arguments"
            )

        arguments = [
            self.evaluate(argument)
            for argument in call.arguments
        ]

        old_scope = self.scope
        old_object = self.current_object

        self.scope = Scope(parent=self.global_scope)
        self.current_object = object_value

        for parameter, argument in zip(
            method.parameters[1:],
            arguments,
        ):
            self.scope.define(
                parameter,
                argument,
            )

        try:
            for statement in method.body:
                self.execute(statement)

        except EmeraldReturn as result:
            return result.value
            
        except (EmeraldSkip, EmeraldStop):
            raise EmeraldRuntimeError(
                "'skip' and 'stop' can only be used inside a loop"
            )
        finally:
            self.scope = old_scope
            self.current_object = old_object

        return None
    def evaluate(self, node):
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, ListLiteral):
            elements = [
                self.evaluate(item)
                for item in node.elements
            ]
            self.check_same_type(elements)
            return elements
        if isinstance(node, UnaryExpression):
            value = self.evaluate(node.operand)

            if node.operator == "not":
                return not self.check_condition(
                    value,
                    "Value after 'not'",
                )

            raise EmeraldRuntimeError(
                f"Unknown unary operator "
                f"'{node.operator}'"
            )
            
        if isinstance(node,IndexAccess):
            collection = self.evaluate(node.collection)
            index = self.evaluate(node.index)
            if not isinstance(collection, list):
                raise EmeraldRuntimeError("Cannot access an index on this value. Expected a List.")
            elif isinstance(index,bool):
                raise EmeraldRuntimeError("Boolean values cannot be used as List indices.")
            elif not isinstance(index, int):
                raise EmeraldRuntimeError("List index must be a whole number.")
            elif index < 1:
                raise EmeraldRuntimeError (f"List index must be at least 1, got {index}.")
            elif index > len(collection):
                raise EmeraldRuntimeError(f"List index out of range. Expected an index between 1 and {len(collection)}, got {index}.")
            else:
                return collection[index-1]
        
        if isinstance(node, AskExpression):
            prompt = self.evaluate(node.prompt)

            while True:
                value = input(prompt)

                if node.input_type is None:
                    return value

                if node.input_type == "str":
                    return value

                if node.input_type == "int":
                    try:
                        return int(value)

                    except ValueError:
                        print("Please enter a whole number.")

                elif node.input_type == "float":
                    try:
                        return float(value)

                    except ValueError:
                        print("Please enter a number.")

                elif node.input_type == "chr":
                    if len(value) == 1:
                        return value

                    print("Please enter a single character.")

                else:
                    raise EmeraldRuntimeError(
                        f"Unknown input type "
                        f"'{node.input_type}'"
                    )
        if isinstance(node, Identifier):
            if node.name == "his":
                if self.current_object is None:
                    raise EmeraldRuntimeError(
                        "'his' can only be used inside a method."
                    )

                return self.current_object

            try:
                return self.scope.get(node.name)

            except KeyError:
                raise EmeraldRuntimeError(
                    f"Undefined variable '{node.name}'"
                )
        if isinstance(node, FunctionCall):
            if node.name in self.classes:
                if node.arguments:
                    raise EmeraldRuntimeError(
                        f"Class '{node.name}' takes no arguments"
                    )

                class_definition = self.classes[
                    node.name
                ]

                return EmeraldObject(
                    class_definition
                )

            return self.call_function(node)
            
        if isinstance(node, MethodCall):
            return self.call_method(node)
            
        if isinstance(node, PropertyAccess):
            object_value = self.evaluate(
                node.object
            )

            if not isinstance(
                object_value,
                EmeraldObject,
            ):
                raise EmeraldRuntimeError(
                    "Property access requires an object."
                )

            if node.property not in object_value.properties:
                raise EmeraldRuntimeError(
                    f"Undefined property "
                    f"'{node.property}'"
                )

            return object_value.properties[
                node.property
            ]

        if isinstance(node, ConcatExpression):
            return "".join(
                format_value(self.evaluate(part))
                for part in node.parts
            )

        if isinstance(node, BinaryExpression):
            left = self.evaluate(node.left)

            if node.operator == "and":
                if not self.check_condition(left, "Left side of 'and'"):
                    return False
                return self.check_condition(
                    self.evaluate(node.right), "Right side of 'and'"
                )

            if node.operator == "or":
                if self.check_condition(left, "Left side of 'or'"):
                    return True
                return self.check_condition(
                    self.evaluate(node.right), "Right side of 'or'"
                )

            right = self.evaluate(node.right)

            if node.operator in {"+", "-", "*", "/", "%"}:
                left_is_number = (
                    isinstance(left, (int, float))
                    and not isinstance(left, bool)
                )

                right_is_number = (
                    isinstance(right, (int, float))
                            and not isinstance(right, bool)
                        )

                if not left_is_number or not right_is_number:
                    if node.operator == "+" and (
                        isinstance(left, str) or isinstance(right, str)
                    ):
                        raise EmeraldRuntimeError(
                            "Cannot use '+' with text. Use & to join text."
                        )
                    raise EmeraldRuntimeError(
                        f"Cannot use '{node.operator}' "
                        f"between these values"
                    )

                try:
                    if node.operator == "+":
                        return left + right

                    if node.operator == "-":
                        return left - right

                    if node.operator == "*":
                        return left * right

                    if node.operator == "/":
                        return left / right
                        
                    if node.operator == "%":
                        return left % right

                except ZeroDivisionError:
                    raise EmeraldRuntimeError(
                        "Cannot divide by zero"
                    )

            raise EmeraldRuntimeError(
                f"Unknown operator "
                f"'{node.operator}'"
            )
        if isinstance(node, ComparisonExpression):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            left_is_number = (
                isinstance(left, (int, float))
                and not isinstance(left, bool)
            )
            right_is_number = (
                isinstance(right, (int, float))
                and not isinstance(right, bool)
            )

            if left_is_number != right_is_number:
                raise EmeraldRuntimeError(
                    "Cannot compare values of different types"
                )

            if node.operator not in COMPARISONS:
                raise EmeraldRuntimeError(
                    f"Unknown comparison operator "
                    f"'{node.operator}'"
                )

            try:
                return COMPARISONS[node.operator](left, right)
            except TypeError:
                raise EmeraldRuntimeError(
                    f"Cannot use '{node.operator}' "
                    f"with these values"
                )

        raise EmeraldRuntimeError(
            f"Cannot evaluate "
            f"{type(node).__name__}"
        )