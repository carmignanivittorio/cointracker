# Vittorio Carmignani, BTC wallet scan

# Database
The schema can be found in Notion.\
**Note**:
 - I have always used  bigint because unsure about using smaller types not knowing the data nature deeply. The same goes also for varchar that may be reduced.
 - I have always used big serial as primary key for simplicity. With more time I would probably use something like this: https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c
 in order to have an id which:
   - has always the same length
   - depends on the sharding key
   - depends on time (so that the rows are ordered)
 - I did not added many available fields (from the API) for simplicity.

## Improvements
Certainly in order to scale we need to create partitions. 
 - A simple idea would be to create them based on the month (since I doubt that users are going to check transactions of a month ago - this 
is something to be checked). You can then have another table 'user_id', 'month', 'n_tx' (only if n_tx > 0) which would tell you exactly in which
partion to look for. 
Of course, we could divide based on any timeframe using the same approach, like: week.


# Download transactions
 - A background process will add the tasks to sync all users by adding a row for each of them inside syncs.
 - The user can add such a row manually or by clicking the button in frontend.
 - A row will not be added if there is already a row for that user either in the "future" or if has been synced recently.
 - The consumer, or better, the workers that syncs the wallets will see the jobs and act accordingly.
   -  It will take the oldest job inserted and start synchronizing the wallets associated with that user (it may prioritize 
 the manual jobs first). Partial indexes on "sync to do" may be useful in order to speed up the process (or move the done
   - syncs into an "old_sync" table).
   -  Once is done, it will update the row in syncs with the new status.
   -  It then picks up the next job and do the same.

## Improvements
- Right now we are just using the blockchain info API. If we implement many others then whenever we finish the tokens in 
one API we could start using another API, in circle (as long as the wrappers work similarly).
- We definetely need to not re-download transactions that have been downloaded before. 
It should download only the transactions till the last update. I did not have time for this.
   

# Tests
## Improvements
 - Some tests cannot run independently from others. Like the ones in the database. Because they
require a user, or wallet etc. This should be taken into account.
 - The tests should be run in a separate thread.
 - We have assumed that all data are valid coming from the api. More checks should be
added before inserting them in the database both at the logic level but also at the database level 
 - (check of the lenght or greater than etc.)
