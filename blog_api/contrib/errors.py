class CustomError(Exception): ...


class DatabaseError(CustomError):
    def __init__(self):
        self.message: str = "Database integrity error"
        super().__init__()


class UnableCreateEntity(CustomError):
    def __init__(self):
        self.message: str = "Unable Create Entity: Field value already exists"
        super().__init__()


class GenericError(CustomError):
    def __init__(self):
        self.message: str = "Generic Error"
        super().__init__()
