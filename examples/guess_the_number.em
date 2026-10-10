secret = 7
tries = 0

redo
    guess = ask "Guess the number (1-10): " int
    tries ++

    if guess == secret
        say "Correct! You needed " & tries & " tries."
        stop
    orif guess < secret
        say "Too low."
    else
        say "Too high."
