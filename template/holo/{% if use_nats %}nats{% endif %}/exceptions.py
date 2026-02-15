from datetime import timedelta


class NakException(Exception):
    delay: int | float = 30  # seconds, 30 = default max_ack_wait
    max_delay = timedelta(minutes=5)

    def __init__(
        self,
        delay: int | float | None = None,  # redelivery is delayed for `delay` seconds
        max_delay: timedelta | None = None,
    ) -> None:
        self.delay = delay or self.delay
        self.max_delay = max_delay or self.max_delay
