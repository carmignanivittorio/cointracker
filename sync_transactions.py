import asyncio

import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed

from btc_api_wrappers.api_objects import Wallet
from btc_api_wrappers.block_chain_info_wrapper import BlockChainInfoWrapper
from btc_api_wrappers.btc_api_wrapper import BTCAPIWrapper
from btc_api_wrappers.rate_limiter import Ratelimiter
from db.main_db import MainDB
from utils import get_async_response


async def _download_and_store_transactions(
        queue: asyncio.Queue, rate_limiter: Ratelimiter, session: aiohttp.ClientSession, db: MainDB,
        api_wrapper: BTCAPIWrapper, address: str, wait_if_not_available_tokens: int = 1
):
    """
    Download and store transactions by building the urls from the queue
    :param queue:
    :param rate_limiter:
    :param session:
    :param db:
    :param api_wrapper:
    :param address:
    :param wait_if_not_available_tokens:
    :return: None
    """
    print_no_tokens: bool = True

    while not queue.empty():
        offset = await queue.get()
        if await rate_limiter.get_token():
            print_no_tokens: bool = True
            url = api_wrapper.get_url(offset=offset, limit=api_wrapper.LIMIT, address=address)
            try:
                response = await get_async_response(url=url, session=session)
            except Exception as e:
                # This is should be handled more specifically based on each status code
                # If the transaction is corrupted this loop will never end, hence we may decide to not put it in the
                # queue again
                print(f'Error getting transactions: {e}')
                queue.put_nowait(url)
            else:
                await _parse_and_store_transactions(response=response, api_wrapper=api_wrapper, db=db)
        else:
            if print_no_tokens:
                print_no_tokens = False
                print('No tokens available, waiting...')
            await asyncio.sleep(wait_if_not_available_tokens)
            queue.put_nowait(offset)
        queue.task_done()


@retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
async def _get_wallet(address: str, api_wrapper: BTCAPIWrapper, session: aiohttp.ClientSession) -> Wallet:
    """
    NOTE that if it fails, it will retry 5 times, then it will raise an exception (with a wait of 4 seconds) (see retry)
    :param address: address to get the wallet of
    :param api_wrapper: API wrapper to use
    :param session: session to use
    :return: Wallet object
    """
    # todo we should wait for the token to be available rather than sleeping
    await asyncio.sleep(api_wrapper.RESET_TOKENS_EVERY_SECONDS)
    response = await get_async_response(url=api_wrapper.get_url(address=address, limit=1), session=session)
    wallet, _ = api_wrapper.parse_response(response=response)
    return wallet


async def update_transactions(wallet_id: int, api_wrapper: BTCAPIWrapper):
    """
    Update the transactions of a wallet
    :param wallet_id: wallet id to update the transactions of
    :param api_wrapper: API wrapper to use
    """
    ratelimiter = Ratelimiter(total_tokens=api_wrapper.TOKENS,
                              reset_tokens_every_seconds=api_wrapper.RESET_TOKENS_EVERY_SECONDS)
    ratelimiter.start()
    queue = asyncio.Queue()
    async with MainDB() as db:
        if await db.is_wallet_need_to_be_scanned(wallet_id=wallet_id):
            address = await db.get_address(wallet_id=wallet_id)
            # avoid that other workers (if any) scan the same wallet
            await db.set_wallet_ongoing_scan(wallet_id=wallet_id, ongoing_scan=True)

            async with aiohttp.ClientSession() as session:
                await api_wrapper.put_all_offsets_in_queue_to_get_all_transactions(address=address, queue=queue,
                                                                                   session=session)
                wallet = await _get_wallet(address=address, api_wrapper=api_wrapper, session=session)
                await db.upsert_wallet(wallet=wallet)
                await _download_and_store_transactions(queue=queue, rate_limiter=ratelimiter, session=session, db=db,
                                                       api_wrapper=api_wrapper, address=address)
            await db.set_wallet_ongoing_scan(wallet_id=wallet_id, ongoing_scan=False, update_last_scan=True)
        else:
            print(f'Wallet {wallet_id} is already up to date')

    ratelimiter.stop()
    ratelimiter.join()


async def _parse_and_store_transactions(response: dict, api_wrapper: BTCAPIWrapper, db: MainDB):
    _, transactions = api_wrapper.parse_response(response=response)
    await db.upsert_transactions(transactions=transactions)
    print(f'Inserted {len(transactions)} transactions')
