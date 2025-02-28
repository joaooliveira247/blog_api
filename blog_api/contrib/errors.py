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
        super().__init__("Unable Update Entity")


class UnableDeleteEntity(CustomError):
    def __init__(self):
        super().__init__("Unable Delete Entity")


class NoResultFound(CustomError):
    def __init__(self, resource: str | None = None):
        message = f"Result not found in {resource}" if resource else "Result not found"
        super().__init__(message)


class GenericError(CustomError):
    def __init__(self):
        super().__init__("Generic Error")
