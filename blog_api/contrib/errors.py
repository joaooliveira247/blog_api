class CustomError(Exception): ...


class DatabaseError(CustomError):
    def __init__(self):
        self.message: str = "Database integrity error"
        super().__init__()
