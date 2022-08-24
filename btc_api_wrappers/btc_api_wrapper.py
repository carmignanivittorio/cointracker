import abc
import asyncio
from typing import Tuple, List

import aiohttp

from btc_api_wrappers.api_objects import Wallet, Transaction


class BTCAPIWrapper(abc.ABC):

    @property
    @abc.abstractmethod
    def LIMIT(self) -> int:
        """
        :return: the limit of transactions to get
        """
        pass

    @property
    @abc.abstractmethod
    def TOKENS(self) -> int:
        """
        :return: number of request per $(RESET_TOKENS_EVERY_SECONDS) seconds
        """
        pass

    @property
    @abc.abstractmethod
    def RESET_TOKENS_EVERY_SECONDS(self) -> int:
        """
        :return: number of seconds to reset the tokens
        """
        pass

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    @abc.abstractmethod
    def get_url(address: str, limit: int = 50, offset: int = 0) -> str:
        """
        :param address: the address to get the transactions from
        :param limit: the number of transactions to get
        :param offset: the offset of the transactions to get
        :return: the url to get the transactions from
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_response(response: dict) -> Tuple[Wallet, List[Transaction]]:
        """
        :param response: the response to parse
        :return: Wallet and list of transactions
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_single_transaction(transaction: dict) -> Transaction:
        """
        Parse a single transaction
        :param transaction: the transaction to parse
        :return: the parsed transaction
        """
        pass

    @staticmethod
    @abc.abstractmethod
    async def put_all_offsets_in_queue_to_get_all_transactions(address: str, queue: asyncio.Queue, session: aiohttp.ClientSession):
        """
        Put all the offset useful to build the url to get the transactions of the given address in the queue
        :param address: the address to get the transactions from
        :param queue: the queue to put the offsets in
        :param session: the aiohttp session to use, this is going to be used once to get the number total of transactions
        """
        pass
