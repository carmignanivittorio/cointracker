# Vittorio Carmignani, BTC wallet scan

# To run it
Run in 1 terminal:
    
```
docker run --rm -P -p 127.0.0.1:5433:5432 -e POSTGRES_PASSWORD="admin" --name pg postgres:alpine
```

in another terminal, install python requirements (assuming you have python 3.9 installed):
    
```
pip install -r requirements.txt
python main.py
```

Wait 10s before running twice main.py or tests because you may get banned and then you need to change IP. 

If you run main.py again, it will tell you that the wallet is already updated (based on the last_scan_at field)

The result will look like:
```
---- Wallet_id 1 wallet bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5 downloading...
Inserted 2 transactions
done
---- Wallet_id 3 wallet 3JptJ5i3d5iSAK3k9QrSZ5qWHdxgHK6nHs downloading...
Inserted 50 transactions
No tokens available, waiting...
Inserted 46 transactions
No tokens available, waiting...
Inserted 50 transactions
No tokens available, waiting...
Inserted 50 transactions
No tokens available, waiting...
Inserted 50 transactions
done
---- Wallet:  Wallet(address='bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5', n_tx=2, total_received=666601, total_sent=666601, final_balance=0) url https://blockchair.com/bitcoin/address/bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5
---- Transactions:  2
0 Transaction(tx_id=1, hash_transaction='27fd4463f3554007a5bde48cb3b2a6e6ce2a687608972ac59ce904bb9cb43191', time=1635331567, size=224, weight=566, fee=429, value=Decimal('-0.00666601')) https://blockchair.com/bitcoin/transaction/27fd4463f3554007a5bde48cb3b2a6e6ce2a687608972ac59ce904bb9cb43191
1 Transaction(tx_id=2, hash_transaction='f6bcb5ddb3ab0b0baaca8f7d16549bad3050ea8d7ebde345d0659777d48f8262', time=1635329801, size=222, weight=561, fee=568, value=Decimal('0.00666601')) https://blockchair.com/bitcoin/transaction/f6bcb5ddb3ab0b0baaca8f7d16549bad3050ea8d7ebde345d0659777d48f8262
---- Wallet:  Wallet(address='3JptJ5i3d5iSAK3k9QrSZ5qWHdxgHK6nHs', n_tx=246, total_received=4065303, total_sent=4065303, final_balance=0) url https://blockchair.com/bitcoin/address/3JptJ5i3d5iSAK3k9QrSZ5qWHdxgHK6nHs
---- Transactions:  246
0 Transaction(tx_id=3, hash_transaction='7686adb4f36d8f264ad888abf6d43de3298f8d3e6460795902c2c3db86e07a4a', time=1661200739, size=65025, weight=138123, fee=69443, value=Decimal('-0.0009')) https://blockchair.com/bitcoin/transaction/7686adb4f36d8f264ad888abf6d43de3298f8d3e6460795902c2c3db86e07a4a
1 Transaction(tx_id=4, hash_transaction='64b0532935924dcedd7421e11b733d3daa31ca58966865e409fe15e6059ffa05', time=1661135933, size=48438, weight=102912, fee=25729, value=Decimal('-0.0002335')) https://blockchair.com/bitcoin/transaction/64b0532935924dcedd7421e11b733d3daa31ca58966865e409fe15e6059ffa05
2 Transaction(tx_id=5, hash_transaction='32f3fef5bd5625effdfaee823ed22f48dea559b8301a8b0b4d53c02d2524a3bc', time=1661127476, size=6101, weight=24077, fee=6080, value=Decimal('0.0009')) https://blockchair.com/bitcoin/transaction/32f3fef5bd5625effdfaee823ed22f48dea559b8301a8b0b4d53c02d2524a3bc
3 Transaction(tx_id=6, hash_transaction='7e2f2bddeb936aa4f87bb17f5333fd6b977d184597c75988764dbc9b2204047c', time=1661099949, size=61433, weight=130499, fee=32626, value=Decimal('-0.0003')) https://blockchair.com/bitcoin/transaction/7e2f2bddeb936aa4f87bb17f5333fd6b977d184597c75988764dbc9b2204047c
...
```
To run the tests:
        
        ```pytest tests/
        ```
It will take around 45s to run the 17 tests.

# Database
The schema can be found in Notion or in db/schema.png
**Note**:
 - I have always used  bigint because unsure about using smaller types not knowing the data nature deeply. The same goes also for varchar, that may be reduced.
 - I have always used big serial as primary key for simplicity. With more time, I would probably use something like this: https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c
 in order to have an id which:
   - has always the same length
   - depends on the sharding key
   - depends on time (so that the rows are ordered)
 - I did not add many available fields (from the API) for simplicity.
 - Note that, on purpose, there is no foreign key between the address in transactions_in_out and the table wallet; because it is certain that we are going to have some addresses that are in transactions that 
we do not care about. 

## Improvements
Certainly in order to scale we need to create partitions. 
 - A simple idea would be to create them based on the month (since I doubt that users are going to check transactions of a month ago - this 
is something to be checked). You can then have another table 'user_id', 'month', 'n_tx' (only if n_tx > 0) which would tell you exactly in which
partion to look for. 
Of course, we could divide based on any timeframe using the same approach, like: week.
 - I am sure other data may be useful in a real application that were ignored here, like the Block data.

# Download transactions
## Background worker
 - A background process will add the tasks to sync all users by adding a row for each of them inside syncs.
 - The user can add such a row manually by clicking the related button in frontend.
 - A row will not be added if there is already a row for that user either in the "future" or if has been synced recently.
 - The consumer, or better, the workers that sync the wallets will see the jobs and act accordingly.
   -  It will take the oldest job inserted and start synchronizing the wallets associated with that user (it may prioritize 
 the manual jobs first). Partial indexes on "sync to do" may be useful in order to speed up the process (or move the done
   - syncs into an "old_sync" table).
   -  Once is done, it will update the row in syncs with the new status.
   -  It then picks up the next job and do the same.
 - Note that parallel worker need to run on different IPs, or have different API tokens in order to not share the same
 - wrapper object.

## How it works now
 - It's available the function to update the transactions of a given wallet.
 - If the wallet was recently updated or the updating is ongoing from another worker, it will not update it again.
 - I implemented a rate limiter using token bucket algorithm. It is not perfect, but it is a good start.
 - The tasks are inserted in a queue (transactions to download) and then a consumer downloads and inserts in the database.

## Improvements
- Right now we are just using the blockchain info API (which is definetely not sustainable - 1 requests/10s). If we implement many others then whenever we finish the tokens in 
one API we could start using another API, in circle (as long as the wrappers work similarly).
- We definitely need to not re-download transactions that have been downloaded before. 
It should download only the transactions till the last update. I did not have time for this.
   

# Tests
## Improvements
 - Some tests cannot run independently from others. Like the ones in the database. Because they
require a user, or wallet etc. This should be taken into account.
 - The tests should be run in a separate thread.
 - We have assumed that all data are valid coming from the api. More checks should be
added before inserting them in the database both at the logic level but also at the database level (check of the lenght or greater than etc.)
 - Here we should create some bitcoin addresses that never change just for the purpose of the tests.
 - We should improve error handling of the API wrapper.
