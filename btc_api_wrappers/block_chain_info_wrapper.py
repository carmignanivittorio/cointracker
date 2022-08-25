import asyncio
from typing import Tuple, List

import aiohttp

from btc_api_wrappers.api_objects import Wallet, TransactionInOut, Transaction
from btc_api_wrappers.btc_api_wrapper import BTCAPIWrapper
from utils import get_async_response


class BlockChainInfoWrapper(BTCAPIWrapper):

    LIMIT = 50
    TOKENS = 1
    RESET_TOKENS_EVERY_SECONDS = 10

    def __init__(self):
        super().__init__(name='BlockChainInfo')

    @staticmethod
    def get_url(address: str, limit: int = 50, offset: int = 0) -> str:
        """
        :param address: the address to get the transactions from
        :param limit: the number of transactions to get
        :param offset: the offset of the transactions to get
        :return: the url to get the transactions from
        """
        return f"https://blockchain.info/rawaddr/{address}?limit={limit}&offset={offset}"

    @staticmethod
    def parse_response(response: dict) -> Tuple[Wallet, List[Transaction]]:
        """
        :param response: the response to parse
        :return: Balance and list of transactions
        """
        balance = Wallet(
            address=response['address'],
            n_tx=response['n_tx'],
            total_received=response['total_received'],
            total_sent=response['total_sent'],
            final_balance=response['final_balance']
        )
        transactions = [
            BlockChainInfoWrapper.parse_single_transaction(
                transaction=transaction,
            ) for transaction in response['txs']
        ]
        return balance, transactions

    @staticmethod
    def parse_single_transaction(transaction: dict) -> Transaction:
        """
        Parse a single transaction
        :param transaction: the transaction to parse
        :return: the parsed transaction
        """
        return Transaction(
            hash_transaction=transaction['hash'],
            time=transaction['time'],
            size=transaction['size'],
            weight=transaction['weight'],
            fee=transaction['fee'],
            inputs=[TransactionInOut(address=input['prev_out']['addr'], value=input['prev_out']['value']) for input
                    in
                    transaction['inputs']],
            outputs=[TransactionInOut(address=output['addr'], value=output['value']) for output in
                     transaction['out']]
        )

    @staticmethod
    async def put_all_offsets_in_queue_to_get_all_transactions(
            address: str, queue: asyncio.Queue, session: aiohttp.ClientSession,
    ):
        """
        Put all the urls to get the transactions of the given address in the queue
        :param address: the address to get the transactions from
        :param queue: the queue to put the urls in
        :param session: the aiohttp session to use
        """
        # todo we should wait for the token to be available rather than sleeping
        await asyncio.sleep(BlockChainInfoWrapper.RESET_TOKENS_EVERY_SECONDS)
        response = await get_async_response(url=BlockChainInfoWrapper.get_url(address=address), session=session)
        number_transactions = response['n_tx']
        # create a link for each page
        for i in range((number_transactions // BlockChainInfoWrapper.LIMIT) + 1):
            queue.put_nowait(i * BlockChainInfoWrapper.LIMIT)
