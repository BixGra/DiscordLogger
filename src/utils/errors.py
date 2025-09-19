class LoggerError(Exception):
    def __init__(self):
        self.error_code = "E00"
        self.status_code = "500"
        self.title = "Unknown Error"

    def __str__(self):
        return f"{self.error_code} : {self.title}"

    def __repr__(self):
        return str(self)


class ServiceNotFoundError(LoggerError):
    def __init__(self):
        self.error_code = "E01"
        self.status_code = "404"
        self.title = "Service not found in monitoring client"


class DuplicateServiceError(LoggerError):
    def __init__(self):
        self.error_code = "E02"
        self.status_code = "400"
        self.title = "Service already in monitoring client"


class RouteNotFoundError(LoggerError):
    def __init__(self):
        self.error_code = "E03"
        self.status_code = "404"
        self.title = "Route not found in monitoring client"


class DuplicateRouteError(LoggerError):
    def __init__(self):
        self.error_code = "E04"
        self.status_code = "400"
        self.title = "Route already in monitoring client"


class PlainHourError(LoggerError):
    def __init__(self):
        self.error_code = "E05"
        self.status_code = "500"
        self.title = "Datetime must be a plain hour (no minutes, seconds, microseconds)"
