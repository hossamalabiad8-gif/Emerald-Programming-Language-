from dataclasses import dataclass


class Node:
    pass


@dataclass
class Program(Node):
    statements: list


@dataclass
class Literal(Node):
    value: object


@dataclass
class Identifier(Node):
    name: str


@dataclass
class VariableDeclaration(Node):
    name: str
    value: Node


@dataclass
class SayStatement(Node):
    values: list

@dataclass
class AskStatement(Node):
    prompt: Node
    variable: str

@dataclass
class BinaryExpression(Node):
    left: Node
    operator: str
    right: Node


@dataclass
class ComparisonExpression(Node):
    left: Node
    operator: str
    right: Node


@dataclass
class UnaryExpression(Node):
    operator: str
    operand: Node


@dataclass
class IfStatement(Node):
    condition: Node
    body: list
    orif_branches: list
    else_body: list

@dataclass
class WhileStatement(Node):
    condition: Node
    body: list

@dataclass
class ForStatement(Node):
    variable: str
    start: Node
    end: Node
    body: list

@dataclass
class FunctionDeclaration(Node):
    name: str
    parameters: list
    body: list


@dataclass
class FunctionCall(Node):
    name: str
    arguments: list
    
@dataclass
class ReturnStatement(Node):
    value: Node
    
@dataclass
class ClassDeclaration(Node):
    name: str
    parent: str | None
    body: list
    
@dataclass
class PropertyAccess(Node):
    object: Node
    property: str

@dataclass
class PropertyAssignment(Node):
    object: Node
    property: str
    value: Node

@dataclass
class MethodCall(Node):
    object: Node
    name: str
    arguments: list

@dataclass
class AskExpression(Node):
    prompt: Node
    input_type: str | None
    
    
    
    
@dataclass
class UpdateExpression(Node):
    variable:Node
    operation:str
    amount : Node | None
    
    
    
@dataclass
class RedoStatement(Node):
    amount: int | None
    body : list[Node]
    
    
@dataclass
class SkipStatement(Node):
    pass


@dataclass
class StopStatement(Node):
    pass

@dataclass
class IndexAssignment(Node):
    collection: Node
    index:Node
    value:Node

@dataclass
class ConcatExpression(Node):
    parts: list

@dataclass
class IndexAccess(Node):
    collection: Node
    index: Node
    
@dataclass
class ListLiteral(Node):
    elements: list[Node]