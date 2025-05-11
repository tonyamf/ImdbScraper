class Phonebook:
    def __init__(self):
        self.entries = {}
    
    def add(self, username, number):
        self.entries[username] = number

    def lookup(self, username):
        return self.entries[username]

    def is_consistent(self):
        return True