import json
from typing import List, Optional

import asyncpg

from btc_api_wrappers.api_objects import Wallet, Transaction, TransactionInOut
from db.db_settings import data


class MainDB:

    def reset_db(self):
        pass

    def __init__(self):
        self.pool = None

    async def ping(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow('SELECT 1')
                assert result['?column?'] == 1, "DB connection failed"

    async def connect(self):
        user = data["USER"]
        pwd = data["PWD"]
        database = data["DATABASE"]
        host = data["HOST"]
        port = data["PORT"]
        sslmode = bool(int(data["SSLMODE"]))

        async def init_connection(conn):
            await conn.set_type_codec('json',
                                      encoder=json.dumps,
                                      decoder=json.loads,
                                      schema='pg_catalog'
                                      )

        self.pool = await asyncpg.create_pool(user=user, password=pwd, database=database, host=host, port=port,
                                              ssl=sslmode, init=init_connection)

        # assert connected
        await self.ping()

    async def close(self):
        await self.pool.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.close()

    async def add_user(self) -> int:
        """
        :return: user_id inserted
        """
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow('INSERT INTO users (user_id) VALUES (default) RETURNING user_id')
                return result['user_id']

    async def user_exists(self, user_id: int) -> bool:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow('SELECT user_id FROM users WHERE user_id = $1', user_id)
                return result is not None

    async def add_user_wallet(self, address: str, user_id: int) -> int:
        """
        :param address: address of the wallet
        :param user_id: user_id of the user to add the wallet to
        :return: wallet_id inserted
        """
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow('INSERT INTO wallets (address) VALUES ($1) '
                                                   'ON CONFLICT DO NOTHING RETURNING wallet_id', address)
                if result is None:
                    result = await connection.fetchrow('SELECT wallet_id FROM wallets WHERE address = $1', address)

                wallet_id = result['wallet_id']
                await connection.execute('INSERT INTO users_wallets (user_id, wallet_id) VALUES ($1, $2)'
                                         'ON CONFLICT DO NOTHING', user_id, wallet_id)
                return wallet_id

    async def add_sync(self, user_id: int, is_manual: bool):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute('INSERT INTO syncs (user_id, is_manual) VALUES ($1, $2)', user_id,
                                         is_manual)

    async def upsert_wallet(self, wallet: Wallet) -> int:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'INSERT INTO wallets (address, n_tx, total_received, total_sent, final_balance) '
                    'VALUES ($1, $2, $3, $4, $5) ON CONFLICT (address) DO UPDATE SET n_tx = $2, '
                    'total_received = $3, total_sent = $4, final_balance = $5 RETURNING wallet_id', wallet.address,
                    wallet.n_tx, wallet.total_received, wallet.total_sent, wallet.final_balance)
                if result is None:
                    result = await connection.fetchrow('SELECT wallet_id FROM wallets WHERE address = $1',
                                                       wallet.address)
                return result['wallet_id']

    async def set_wallet_ongoing_scan(self, ongoing_scan: bool, wallet_id: int, update_last_scan: bool = True):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                if not ongoing_scan and update_last_scan:
                    # we just finished the scan and we update last scan
                    await connection.execute('UPDATE wallets SET ongoing_scan = FALSE, '
                                             'last_scan_at = CURRENT_TIMESTAMP WHERE wallet_id = $1', wallet_id)
                else:
                    await connection.execute('UPDATE wallets SET ongoing_scan = $1 WHERE wallet_id = $2',
                                             ongoing_scan, wallet_id)

    async def is_wallet_need_to_be_scanned(self, wallet_id: int) -> bool:
        """
        :param wallet_id:
        :return: True if:
            - the wallet is not ongoing scan
            - the wallet was not scanned in the last hour
        """
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    "SELECT (wallets.ongoing_scan IS NULL OR NOT wallets.ongoing_scan) AND ("
                    "   wallets.last_scan_at IS NULL OR ((now() - interval '60 min') > wallets.last_scan_at) ) "
                    "as to_be_scanned "
                    "FROM wallets WHERE wallet_id = $1",
                    wallet_id)
                if not result:
                    return False
                return result['to_be_scanned']

    async def upsert_transactions(self, transactions: List[Transaction]):
        """
        :param transactions: list of transactions to insert (ordered by time)
        """
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                for transaction in transactions:
                    result = await connection.fetchrow(
                        'INSERT INTO transactions (hash_transaction, time, size, weight, fee) '
                        'VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING RETURNING tx_id',
                        transaction.hash_transaction, transaction.time, transaction.size,
                        transaction.weight, transaction.fee,
                    )
                    if result is None:
                        # the transaction is already in the db
                        continue
                    transactions_id = result['tx_id']
                    await self.__add_transaction_in_out(transaction.inputs, True, transactions_id, connection)
                    await self.__add_transaction_in_out(transaction.outputs, False, transactions_id, connection)

    @staticmethod
    async def __add_transaction_in_out(
            transactions_in_out: list[TransactionInOut],
            is_input: bool,
            transaction_id: int,
            connection
    ):
        values = [(transaction_id, is_input, transaction_in_out.address, transaction_in_out.value)
                  for transaction_in_out in transactions_in_out]
        await connection.executemany(
            'INSERT INTO transactions_in_out (tx_id, is_input, address, value) VALUES ($1, $2, $3, $4)', values
        )

    async def get_wallet_transactions(self, address: str) -> dict:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(
                    """
                    SELECT transactions_values.tx_id, transactions_values.value, hash_transaction, "time", size, 
                    weight, fee
                    FROM (
                        SELECT tx_id, sum(CASE WHEN is_input THEN -value ELSE value END) as value
                        FROM transactions_in_out
                        where address = $1
                        GROUP BY tx_id
                    ) transactions_values INNER JOIN transactions 
                    ON transactions.tx_id = transactions_values.tx_id
                    ORDER BY transactions.time DESC
                    """,
                    address
                )
                return result

    async def get_address(self, wallet_id: str) -> Optional[str]:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow('Select address from wallets where wallet_id = $1', wallet_id)
                if result is None:
                    return None
                return result['address']
