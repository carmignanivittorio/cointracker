import asyncio

import aiohttp
import pytest

from btc_api_wrappers.api_objects import Transaction
from btc_api_wrappers.block_chain_info_wrapper import BlockChainInfoWrapper
from tests.values_tests import transaction_test, wallet_246, wallet_2
from utils import get_async_response

# TODO
#  1. here we should create some bitcoin addresses that never change
#   just for the purpose of these tests.
#  2. it is assumed the rate limiter is in place, otherwise the tests will fail (because there is no
#   error handling if the 3rd party API fails)



block_chain_info_wrapper = BlockChainInfoWrapper()
LIMIT: int = 50


def test_get_url():
    assert block_chain_info_wrapper.get_url(wallet_246.address,
                                            limit=LIMIT) == f'https://blockchain.info/rawaddr/{wallet_246.address}?limit={LIMIT}&offset=0'


@pytest.mark.asyncio
async def test_parse_response():
    async with aiohttp.ClientSession() as session:
        response = await get_async_response(
            url=BlockChainInfoWrapper.get_url(address=wallet_2.address), session=session
        )

        wallet, transactions = BlockChainInfoWrapper.parse_response(response)
        assert wallet.address == wallet_2.address
        assert len(transactions) == wallet_2.n_tx
        assert wallet.final_balance == wallet_2.final_balance
        balance_from_transactions = 0

        for transaction in transactions:
            for tr_input in transaction.inputs:
                if tr_input.address == wallet_2:
                    balance_from_transactions -= tr_input.value

            for tr_output in transaction.outputs:
                if tr_output.address == wallet_2:
                    balance_from_transactions += tr_output.value

        assert wallet.final_balance == balance_from_transactions


@pytest.mark.asyncio
async def test_parse_single_transaction():
    transaction = transaction_test
    parsed_transaction: Transaction = block_chain_info_wrapper.parse_single_transaction(transaction)
    # assert transaction is parsed correctly
    assert transaction['hash'] == parsed_transaction.hash_transaction
    assert transaction['time'] == parsed_transaction.time
    assert transaction['weight'] == parsed_transaction.weight
    assert transaction['fee'] == parsed_transaction.fee
    inputs = transaction['inputs']
    outputs = transaction['out']
    assert len(inputs) == len(parsed_transaction.inputs)
    assert len(outputs) == len(parsed_transaction.outputs)

    for input_v, parse_input in zip(inputs, parsed_transaction.inputs):
        assert input_v['prev_out']['addr'] == parse_input.address
        assert input_v['prev_out']['value'] == parse_input.value

    for output, parse_output in zip(outputs, parsed_transaction.outputs):
        assert output['addr'] == parse_output.address
        assert output['value'] == parse_output.value


@pytest.mark.asyncio
async def test_put_all_urls_in_queue_to_get_all_transactions():
    deque = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        await block_chain_info_wrapper.put_all_offsets_in_queue_to_get_all_transactions(wallet_246.address, deque,
                                                                                        session)
        size_now = deque.qsize()
        assert size_now >= (wallet_2.n_tx / LIMIT)  # other transactions may be added

        first_element = await deque.get()
        assert first_element == block_chain_info_wrapper.get_url(wallet_246.address)

        while not deque.empty():
            last_element = await deque.get()

        assert last_element == block_chain_info_wrapper.get_url(
            wallet_246.address, offset=(size_now * LIMIT) - LIMIT, limit=LIMIT
        )
