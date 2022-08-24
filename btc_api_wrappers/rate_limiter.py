import threading
import time

from utils import async_lock


class Ratelimiter(threading.Thread):

    """
    This is a rate limiter based on time.
    Every time a token is requested, it checks if there are available tokens.
    If there are, it returns True and decrements the available tokens.
    If there are not, it returns False.
    Every X seconds, it resets the available tokens to the total tokens.
    """

    def __init__(self, total_tokens: int = 3, reset_tokens_every_seconds: int = 3):
        super().__init__(name='RateLimiter', daemon=True)
        assert total_tokens > 0, "Total tokens must be greater than 0"
        assert reset_tokens_every_seconds >= 0, "Reset tokens every seconds must be >= 0"
        self.token_lock = threading.Lock()
        self.total_tokens: int = total_tokens
        self.available_tokens: int = 0
        self.reset_tokens_every_seconds: int = reset_tokens_every_seconds
        self.event: threading.Event = threading.Event()

    def stop(self):
        """
        Stop the thread
        """
        self.event.set()

    async def get_token(self) -> bool:
        """
        :return: True if there are available tokens, False otherwise
        """
        async with async_lock(self.token_lock):
            if self.available_tokens > 0:
                self.available_tokens -= 1
                return True
            else:
                return False

    def run(self) -> None:
        """
        Reset the available tokens every $(self.reset_tokens_every_seconds) seconds
        """
        while self.event.is_set() is False:
            time.sleep(self.reset_tokens_every_seconds)
            with self.token_lock:
                self.available_tokens = self.total_tokens
