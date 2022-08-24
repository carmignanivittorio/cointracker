# Vittorio Carmignani, BTC wallet scan

# To run it
Run in 1 terminal:
    
    ```docker run --rm -P -p 127.0.0.1:5433:5432 -e POSTGRES_PASSWORD="admin" --name pg postgres:alpine

in another terminal, install python requirements:
    
    ```pip install -r requirements.txt
       python main.py
    ```
To run the tests:
        
        ```pytest tests/
        ```
Wait 10s before running twice main.py or tests because you may get banned and then you need to change IP.

# Database
The schema can be found in Notion or in db/schema.png
**Note**:
 - I have always used  bigint because unsure about using smaller types not knowing the data nature deeply. The same goes also for varchar that may be reduced.
 - I have always used big serial as primary key for simplicity. With more time I would probably use something like this: https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c
 in order to have an id which:
   - has always the same length
   - depends on the sharding key
   - depends on time (so that the rows are ordered)
 - I did not added many available fields (from the API) for simplicity.
 - Note that on purpose the there is no foreign key between the address in transactions_in_out and
and the table wallet because it is certain that we are going to have some addresses that are in transactions but
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
 - 
   

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
added before inserting them in the database both at the logic level but also at the database level 
 - (check of the lenght or greater than etc.)
- here we should create some bitcoin addresses that never change just for the purpose of the tests.
 - We should improve error handling of the API wrapper.
