class RetryPolicy:
    def __init__(self, max_attempts=3):
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self.max_attempts = max_attempts

    def run(self, operation, retryable):
        last_error = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return operation()
            except Exception as exc:
                last_error = exc
                if not retryable(exc) or attempt == self.max_attempts:
                    raise
        raise last_error
