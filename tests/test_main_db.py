import datetime
import random

import aiohttp
import pytest

from btc_api_wrappers.api_objects import Wallet
from btc_api_wrappers.block_chain_info_wrapper import BlockChainInfoWrapper
from db.main_db import MainDB
from tests.utils_tests import get_random_string
from tests.values_tests import wallet_2
from utils import get_async_response


@pytest.fixture
def random_wallet() -> Wallet:
    return Wallet(final_balance=150, total_received=100, total_sent=50, n_tx=10, address=get_random_string(
        length=random.randint(34, 42)))


@pytest.mark.asyncio
async def test_ping():
    async with MainDB() as db:
        await db.ping()
        assert True


@pytest.mark.asyncio
async def test_add_user():
    async with MainDB() as db:
        user_id = await db.add_user()
        assert await db.user_exists(user_id)


@pytest.mark.asyncio
async def test_user_exists():
    async with MainDB() as db:
        assert await db.user_exists(1)
        assert not await db.user_exists(200)


@pytest.mark.asyncio
async def test_add_user_wallet():
    wallet_address = get_random_string(random.randint(34, 45))
    user_id = 1
    async with MainDB() as db:
        wallet_id = await db.add_user_wallet(address=wallet_address, user_id=user_id)
        assert wallet_id > 0
        async with db.pool.acquire() as connection:
            result = await connection.fetchrow('SELECT wallet_id FROM wallets WHERE address = $1', wallet_address)
            assert result['wallet_id'] == wallet_id
            result = await connection.fetchrow(
                'SELECT wallet_id FROM users_wallets WHERE wallet_id = $1 AND user_id = $2',
                wallet_id, user_id)
            assert result['wallet_id'] == wallet_id


@pytest.mark.asyncio
async def test_add_sync():
    user_id = 1
    is_manual = True
    async with MainDB() as db:
        await db.add_sync(user_id, is_manual)
        async with db.pool.acquire() as connection:
            result = await connection.fetchrow('SELECT user_id FROM syncs WHERE user_id = $1 AND is_manual = $2',
                                               user_id, is_manual)
            assert result['user_id'] == user_id


@pytest.mark.asyncio
async def test_upsert_wallet(random_wallet: Wallet):
    async with MainDB() as db:
        wallet_id = await db.upsert_wallet(random_wallet)
        async with db.pool.acquire() as connection:
            result = await connection.fetchrow('SELECT * FROM wallets WHERE wallet_id = $1', wallet_id)
            assert result['final_balance'] == 150
            assert result['total_received'] == 100
            assert result['total_sent'] == 50
            assert result['n_tx'] == 10


@pytest.mark.asyncio
async def test_set_wallet_ongoing_scan(random_wallet: Wallet):
    async with MainDB() as db:
        wallet_id = await db.upsert_wallet(random_wallet)
        await db.set_wallet_ongoing_scan(wallet_id=wallet_id, ongoing_scan=True)
        async with db.pool.acquire() as connection:
            result = await connection.fetchrow('SELECT ongoing_scan FROM wallets WHERE wallet_id = $1', wallet_id)
            assert result['ongoing_scan']
            await db.set_wallet_ongoing_scan(wallet_id=wallet_id, ongoing_scan=False, update_last_scan=True)
            result = await connection.fetchrow('SELECT ongoing_scan, last_scan_at FROM wallets WHERE wallet_id = $1',
                                               wallet_id)
            assert not result['ongoing_scan']
            # assert last_scan_at is not older than 10 seconds
            assert datetime.datetime.now(tz=datetime.timezone.utc) - result['last_scan_at'] < datetime.timedelta(
                seconds=10)


@pytest.mark.asyncio
async def test_is_wallet_need_to_be_scanned(random_wallet):
    async with MainDB() as db:
        wallet_id = await db.upsert_wallet(random_wallet)
        result = await db.is_wallet_need_to_be_scanned(wallet_id)
        assert result
        await db.set_wallet_ongoing_scan(wallet_id=wallet_id, ongoing_scan=True)
        result = await db.is_wallet_need_to_be_scanned(wallet_id)
        assert not result
        await db.set_wallet_ongoing_scan(wallet_id=wallet_id, ongoing_scan=False, update_last_scan=True)
        result = await db.is_wallet_need_to_be_scanned(wallet_id)
        assert not result


@pytest.mark.asyncio
async def test_upsert_transactions():
    async with MainDB() as db:
        async with aiohttp.ClientSession() as session:
            response = await get_async_response(
                url=BlockChainInfoWrapper.get_url(address=wallet_2.address), session=session
            )
            _, transactions = BlockChainInfoWrapper.parse_response(response)

        await db.upsert_transactions(transactions)
        async with db.pool.acquire() as connection:
            for transaction in transactions:
                result = await connection.fetchrow(
                    'SELECT * FROM transactions WHERE hash_transaction = $1', transaction.hash_transaction
                )
                # we just assert the value was inserted
                assert result['hash_transaction'] == transaction.hash_transaction
                result = await connection.fetch(
                    'SELECT * FROM transactions_in_out WHERE tx_id = $1', result['tx_id']
                )
                assert len(result) == len(transaction.inputs) + len(transaction.outputs)
                # todo assert the values are correct, one by one


@pytest.mark.asyncio
async def test_get_wallet_transactions():
    # NOTE here we assume that the transactions of wallet 2 are already inserted in the database
    async with MainDB() as db:
        result = await db.get_wallet_transactions(address=wallet_2.address)
        assert len(result) == 2
        assert sum([transaction['value'] for transaction in result]) == wallet_2.final_balance


@pytest.mark.asyncio
async def test_get_address(random_wallet: Wallet):
    async with MainDB() as db:
        wallet_id = await db.upsert_wallet(random_wallet)
        result = await db.get_address(wallet_id)
        assert result == random_wallet.address
