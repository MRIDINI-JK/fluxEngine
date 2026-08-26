from croniter import croniter
from datetime import datetime


class CronParser:

    @staticmethod
    def validate(
        expression: str,
    ) -> bool:

        return croniter.is_valid(
            expression
        )

    @staticmethod
    def next_run(
        expression: str,
        base_time: datetime,
    ) -> datetime:

        if not CronParser.validate(
            expression
        ):
            raise ValueError(
                f"Invalid cron expression: "
                f"{expression}"
            )

        iterator = croniter(
            expression,
            base_time,
        )

        return iterator.get_next(
            datetime
        )