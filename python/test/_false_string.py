class AlwaysFalseString(str):
    def __new__(cls, value):
        return super(AlwaysFalseString, cls).__new__(cls, value)
    
    def __bool__(self):
        return False
