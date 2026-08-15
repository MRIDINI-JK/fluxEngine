from dataclasses import dataclass


@dataclass
class RetryPolicy:

    max_attempts: int = 3

    initial_delay: float = 1.0

    max_delay: float = 30.0

    backoff_factor: float = 2.0

    def should_retry(
        self,
        attempts: int,
    ) -> bool:

        return attempts < self.max_attempts

    def get_delay(
        self,
        attempts: int,
    ) -> float:

        delay = (
            self.initial_delay
            * (
                self.backoff_factor
                ** max(attempts - 1, 0)
            )
        )

        return min(
            delay,
            self.max_delay,
        )