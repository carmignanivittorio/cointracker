import asyncio

from btc_api_wrappers.rate_limiter import Ratelimiter


def test_rate_limiter():
    total_tokens = 3
    reset = 6
    ratelimiter = Ratelimiter(total_tokens=total_tokens,
                              reset_tokens_every_seconds=reset)
    ratelimiter.start()

    print('Total Tokens', total_tokens, 'Reset', reset)

    async def test_get_token():
        for i in range(reset):
            assert not (await ratelimiter.get_token())
            print('Not available: OK', i)
            await asyncio.sleep(1)
        for i in range(total_tokens):
            print('Available: OK', i)
            assert (await ratelimiter.get_token())
        for i in range(reset):
            print('Not available: OK', i)
            assert not (await ratelimiter.get_token())
            await asyncio.sleep(1)

    asyncio.run(test_get_token())
    ratelimiter.stop()
    ratelimiter.join()

    print('Test OK')


if __name__ == '__main__':
    test_rate_limiter()
    print('done')
