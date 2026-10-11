# 💚 Emerald

**A small, readable programming language with no colons, no `def`, and a Minecraft soul.**
Emerald (short name: *Emelang*) is an experimental language built from scratch in Python. Its identity is inspired by the emerald from Minecraft, but its syntax is entirely its own.

## Why Emerald?

- **Indentation-based blocks.** No `:` at the end of lines.
- **No type declarations.** Types are inferred from values.
- **Short keywords.** `say` to print, `ask` to read input, `orif` instead of `elif`.
- **Functions without `def`.** Just write the name and indent the body.
- **Classes with inheritance.** `class Dog Animal`, and `his` instead of `self`.
- **Clear error messages** with line numbers.

## A first look

```emerald
name = ask "What is your name? " str
say "Hello, " & name & "!"

for i in 1 to 3
    say "Emerald " & i
```

Output:

```
What is your name? Hossam
Hello, Hossam!
Emerald 1
Emerald 2
Emerald 3
```

## Requirements

Python **3.10 or newer**.

## Running a program

Emerald files use the `.em` extension.

```bash
python -m main hello.em
```

## Language Guide

### Variables and types

No type declarations. Just assign.

```
name = "Hossam"
age = 15
height = 175.5
letter = 'A'
alive = true
nothing_here = null
```

Emerald has strings (`"text"`), integers, floats, characters (`'A'`), booleans (`true` / `false`), `null`, and lists. Assigning again to an existing name changes its value.

Strings support these escapes: `\n` (new line), `\t` (tab), `\"`, `\'`, and `\\`.

### Comments

A comment starts with `!`.

```
! This is a comment
say "Hello"
```

A `!` inside a string stays part of the string. (`!=` is the "not equal" operator, not a comment.)

### Output: `say`

```
say "Hello Emerald!"
```

Join values with `&`. Any value can be joined, and no spaces are added for you:

```
say "Name: " & name & ", age: " & age
say "Total: " & 2 + 3
```

`null` prints as `nothing`, booleans print as `true` / `false`, and lists print like `[1, 2, 3]`.

### Input: `ask`

As a statement, `ask` stores the typed text in a variable:

```
ask "What is your name? " name
```

As a value, you can request a type. If the input doesn't match, Emerald asks again instead of crashing:

```
name = ask "Name: " str
age = ask "Age: " int
height = ask "Height: " float
letter = ask "Letter: " chr
```

### Arithmetic

```
say 10 + 5     ! 15
say 10 - 3     ! 7
say 4 * 5      ! 20
say 10 / 4     ! 2.5
say 10 % 3     ! 1
say -5 + 2     ! -3
```

Division always gives a float, and dividing by zero is a clear runtime error. `*`, `/`, `%` run before `+` and `-`, and parentheses work as usual:

```
say 2 + 3 * 4      ! 14
say (2 + 3) * 4    ! 20
```

`+` is for numbers only. To join text, use `&`.

### Increase and decrease

```
count = 0
count ++        ! 1
count ++ 5      ! 6
count --        ! 5
count -- 2      ! 3
```

This also works on object properties (`hero.hp ++ 10`) and list items (`scores[1] -- 1`).

### Comparisons

`==`, `!=`, `>`, `<`, `>=`, `<=`

```
age = 15
say age > 10      ! true
say age == 16     ! false
```

Numbers compare with numbers and text with text. Comparing a number with something that isn't a number is an error.

### Booleans and logic

`and`, `or`, `not`. Both `and` and `or` short-circuit.

```
if age > 10 and age < 20
    say "Teen"
```

Conditions must be exactly `true` or `false`. Emerald has no "truthy" or "falsy" values, so write `x != 0` instead of just `x`.

### Conditions: `if`, `orif`, `else`

```
if age > 18
    say "Adult"
orif age == 18
    say "Exactly 18"
else
    say "Young"
```

You can use as many `orif` branches as you like. Only the first true branch runs.

### Loops

**`while`** repeats as long as the condition is `true`:

```
counter = 1
while counter <= 5
    say counter
    counter ++
```

**`for`** counts through a range. Both ends are included, and it counts down automatically when the start is bigger than the end:

```
for i in 1 to 3
    say i          ! 1 2 3

for i in 3 to 1
    say i          ! 3 2 1
```

**`redo`** repeats a block a fixed number of times, or forever if you give no number:

```
redo 3
    say "Hi"
```

**`skip`** jumps to the next round and **`stop`** leaves the loop. Using them outside a loop is an error.

```
for i in 1 to 5
    if i == 2
        skip
    if i == 4
        stop
    say i          ! 1 3
```

### Functions

No `def` keyword. Write the name with parentheses, then indent the body.

```
hello()
    say "Hello"

add(a, b)
    return a + b

hello()
say add(10, 20)
```

A function must be defined before it is called. `return` ends the function immediately, and a function without `return` gives back `null`.

**Scope:** a function can read and change global variables. A name that doesn't exist yet is created inside the function and disappears when it ends. Variables created inside a `for` loop also stay inside that loop.

```
total = 0
add_to_total(n)
    total = total + n

add_to_total(5)
say total          ! 5
```

### Classes

```
class Person
    greet(his, name)
        say "Hello, " & name & "! I am " & his.name

person = Person()
person.name = "Hossam"
person.greet("Sara")
```

- `his` is Emerald's `self`. It must be the first parameter of every method.
- Objects are created with `ClassName()`. Properties are added by assigning to them.
- Reading a property that was never set is an error.

### Inheritance

Write the parent's name after the class name:

```
class Animal
    speak(his)
        say his.name & " makes a sound"

class Dog Animal
    speak(his)
        say his.name & " barks"

class Cat Animal

dog = Dog()
dog.name = "Rex"
dog.speak()        ! Rex barks

cat = Cat()
cat.name = "Mimi"
cat.speak()        ! Mimi makes a sound
```

A child can override methods, and lookup climbs through any number of levels.

### Lists

```
numbers = [10, 20, 30]
say numbers[1]         ! 10 (indexes start at 1)
numbers[2] = 99
say numbers           ! [10, 99, 30]
numbers[3] ++ 5
empty = []
```

- A list holds **one type only**. `[1, "two"]` and `[1, 2.5]` are errors, and so is assigning a value of another type into a list.
- A list must be written on a single line.
- Using an index outside the list is an error that tells you the valid range.

## Things worth knowing

- **Indentation** uses spaces. Tabs are not allowed, and each block must be indented consistently.
- **Lists** hold one type and are written on a single line. Indexes start at **1**.
- **Conditions** must be `true` or `false`. There is no truthy or falsy.
- **Text** is joined with `&`. `+` works on numbers only.
- **Functions** must be defined before they are called.
- **Errors** show the line number when they happen at runtime, and `line:column` for syntax errors.

```
Emerald Runtime Error at line 4: Undefined variable 'y'
Emerald Syntax Error: Expected RPAREN at 3:12
```

## Project structure

```
Emerald/
├── main.py          ! entry point
├── lexer.py         ! source code -> tokens
├── parser.py        ! tokens -> AST
├── emerald_ast.py   ! AST node definitions
├── interpreter.py   ! runs the AST
├── scope.py         ! variable scopes
├── errors.py        ! Emerald error types
└── examples/        ! sample programs
```

The pipeline:

```
Source -> Lexer -> Tokens -> Parser -> AST -> Interpreter
```

The **interpreter** is Emerald's main engine and gets new features first. The bytecode compiler and VM are **experimental**.

## Status and roadmap

Emerald is a young, evolving language. Planned:

- `do` / `hook` error handling
- **Garden** (`[[...]]`): collections that can mix types, plus `each`, `has`, and list functions like `add`
- `glob!`
- Documentation blocks (`#| ... |#`)
- `within`, `as`, `is`
- A module system: `visit`, `at`, `tag`, `village`
- A built-in Minecraft library
- VS Code extension: autocomplete, diagnostics, debugger

## License

MIT License. Copyright (c) 2026 Hossam Sabry El-Abyad.
