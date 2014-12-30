class DashboardException(Exception):
    """Base Exception for the project
    To correctly use this class, inherit from it and define
    the 'message' property.
    """

    message = "An unknown exception occurred"

    def __str__(self):
        return self.message

    def __init__(self):
        super(DashboardException, self).__init__(self.message)


class NotFound(DashboardException):
    message = "Object not found"

    def __init__(self, message=None):
        if message:
            self.message = message


class DuplicateEntry(DashboardException):
    message = "Database object already exists"

    def __init__(self, message=None):
        if message:
            self.message = message
