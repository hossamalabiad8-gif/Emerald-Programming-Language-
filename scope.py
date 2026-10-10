class Scope:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent
    def define(self, name, value):
        self.values[name] = value
    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise KeyError(name)
    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        raise KeyError(name)
    def set(self, name, value):
        scope = self
        while scope is not None:
            if name in scope.values:
                scope.values[name] = value
                return
            scope = scope.parent
        self.values[name] = value