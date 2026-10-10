class Animal
    speak(his)
        say his.name & " makes a sound"

class Dog Animal
    speak(his)
        say his.name & " says Woof!"

class Cat Animal

dog = Dog()
dog.name = "Rex"
dog.speak()

cat = Cat()
cat.name = "Mimi"
cat.speak()
