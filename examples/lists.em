scores = [10, 20, 30]

total = 0
for i in 1 to 3
    total = total + scores[i]

say "Scores: " & scores
say "Total: " & total
say "Average: " & total / 3

scores[2] = 25
say "After change: " & scores
