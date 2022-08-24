import asyncio

import attr

from btc_api_wrappers.block_chain_info_wrapper import BlockChainInfoWrapper
from db.main_db import MainDB
from sync_transactions import update_transactions

if __name__ == '__main__':

    @attr.s(frozen=True)
    class Transaction:
        # this is just to print
        tx_id = attr.ib()
        hash_transaction: str = attr.ib()
        time: int = attr.ib(validator=attr.validators.instance_of(int))
        size: int = attr.ib(validator=attr.validators.instance_of(int))
        weight: int = attr.ib(validator=attr.validators.instance_of(int))
        fee: int = attr.ib(validator=attr.validators.instance_of(int))
        value: int = attr.ib(converter=lambda x: x / 100000000)

        @property
        def url(self):
            return f"https://blockchair.com/bitcoin/transaction/{self.hash_transaction}"

    async def create_db_and_get_transactions():
        async with MainDB() as db:
            user_id = await db.add_user()

            wallet_2 = 'bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5'
            wallet_246 = '3JptJ5i3d5iSAK3k9QrSZ5qWHdxgHK6nHs'
            wrapper = BlockChainInfoWrapper()
            for wallet in [wallet_2, wallet_246]:
                wallet_id = await db.add_user_wallet(address=wallet, user_id=user_id)
                print('---- Wallet_id', wallet_id, 'wallet', wallet, 'downloading...')
                await update_transactions(wallet_id, wrapper)
                print('done')

        async with MainDB() as db:
            print('---- Wallet: ', wallet, 'url', f'https://blockchair.com/bitcoin/address/{wallet}')
            transactions = await db.get_wallet_transactions(wallet)
            print('---- Transactions: ', len(transactions))
            for i, transaction in enumerate(transactions):
                tr = Transaction(**transaction)
                print(i, tr, tr.url)


    asyncio.run(create_db_and_get_transactions())
    print('done')
