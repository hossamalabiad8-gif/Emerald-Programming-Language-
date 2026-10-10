say "Emerald Calculator"
a = ask "First number: " float
b = ask "Second number: " float

say a & " + " & b & " = " & a + b
say a & " * " & b & " = " & a * b

if b != 0
    say a & " / " & b & " = " & a / b
else
    say "Cannot divide by zero"
