from typing import List

import attr


@attr.s(frozen=True)
class Wallet:
    address: str = attr.ib()
    n_tx: int = attr.ib()
    total_received: int = attr.ib()
    total_sent: int = attr.ib()
    final_balance: int = attr.ib()


@attr.s(frozen=True)
class TransactionInOut:
    address: str = attr.ib()
    value: int = attr.ib()


@attr.s(frozen=True)
class Transaction:
    hash_transaction: str = attr.ib(validator=attr.validators.instance_of(str))
    time: int = attr.ib(validator=attr.validators.instance_of(int))
    size: int = attr.ib(validator=attr.validators.instance_of(int))
    weight: int = attr.ib(validator=attr.validators.instance_of(int))
    fee: int = attr.ib(validator=attr.validators.instance_of(int))
    inputs: List[TransactionInOut] = attr.ib(validator=attr.validators.instance_of(list))
    outputs: List[TransactionInOut] = attr.ib(validator=attr.validators.instance_of(list))
