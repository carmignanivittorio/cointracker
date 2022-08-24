import asyncio
import contextlib

import aiohttp


async def get_async_response(url: str, session: aiohttp.ClientSession) -> dict:
    """
    Get the transactions of a given address
    :param url: the url to get the transactions from
    :param session: the aiohttp session to use
    :return: the transactions of the given address
    """
    async with session.get(url) as response:
        assert response.status == 200, f'Error getting reponse: {response}'
        return await response.json()


@contextlib.asynccontextmanager
async def async_lock(lock):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lock.acquire)
    try:
        yield  # the __lock is held
    finally:
        lock.release()
