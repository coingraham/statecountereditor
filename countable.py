

class Countable:

    total = 0

    def __init__(self, resource, name):
        Countable.total += 1
        self.resource = resource
        self.name = name
        self.max = 0

    def push(self, number):
        number = int(number)
        if number > self.max:
            self.max = number

    def get_full_name(self):
        full_name = self.resource + "." + self.name
        return full_name

    def get_max(self):
        return int(self.max) + 1
