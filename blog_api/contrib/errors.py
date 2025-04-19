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


class NothingToUpdate(CustomError):
    def __init__(self):
        super().__init__("Nothing to update")


class UnableDeleteEntity(CustomError):
    def __init__(self):
        super().__init__("Unable Delete Entity")


class NoResultFound(CustomError):
    def __init__(self, resource: str | None = None):
        message = (
            f"Result not found with {resource}" if resource else "Result not found"
        )
        super().__init__(message)


class CacheError(CustomError):
    def __init__(self, message: str):
        super().__init__(message)


class EncodingError(CustomError):
    def __init__(self):
        super().__init__("Error when try encoding one object")


class TokenError(CustomError):
    def __init__(self, message: Exception | None = None):
        custom_msg = f"Token Error: {str(message)}" if message else "Token Error"
        super().__init__(custom_msg)


class InvalidResource(CustomError):
    def __init__(self, message: str | None):
        super().__init__(f"{message} invalid" if message else "invalid Resource")


class GenericError(CustomError):
    def __init__(self, message: Exception | str | None = None):
        custom_message = str(message) if message else "Generic Error"
        super().__init__(custom_message)
