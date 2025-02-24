class CustomError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DatabaseError(CustomError):
    def __init__(self):
        super().__init__("Database integrity error")


class UnableCreateEntity(CustomError):
    def __init__(self):
        super().__init__("Unable Create Entity: Field value already exists")


class UnableUpdateEntity(CustomError):
    def __init__(self):
        super().__init__("Unable Create Entity: Field value already exists")


class NoResultFound(CustomError):
    def __init__(self):
        super().__init__("Result not found")


class GenericError(CustomError):
    def __init__(self):
        super().__init__("Generic Error")
