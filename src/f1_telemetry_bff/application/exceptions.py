class ApplicationError(Exception):
    """Base exception for application errors."""


class SessionNotFoundError(ApplicationError):
    """Raised when a requested session is not found."""

    def __init__(self, session_key: int) -> None:
        self.session_key = session_key
        super().__init__(f"Session with key {session_key} not found")


class DriverNotFoundError(ApplicationError):
    """Raised when a requested driver is not found in a session."""

    def __init__(self, driver_number: int, session_key: int) -> None:
        self.driver_number = driver_number
        self.session_key = session_key
        super().__init__(f"Driver {driver_number} not found in session {session_key}")


class SameDriverSelectedError(ApplicationError):
    """Raised when the same driver is selected for both sides of comparison."""

    def __init__(self, driver_number: int) -> None:
        self.driver_number = driver_number
        super().__init__(f"Driver A and Driver B cannot be the same driver ({driver_number})")
