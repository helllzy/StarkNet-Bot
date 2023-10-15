from random import choice, randint, uniform
from string import hexdigits

from starknet_py.contract import Contract

from config import AMOUNT_TO_KEEP
from modules.utils import exec
from data.data import (
    DMAIL_ADDRESS,
    DMAIL_ABI,
    ETH_ADDRESS,
    TOKENS_ABI,
    UNFRAMED_ADDRESS,
    FLEX_ADDRESS,
    Module
)


class Transaction(Contract, Module):
    def __init__(self, account):
        self.account = account


    async def start(self, module) -> int:
        match module:
            case "dmail":
                txn = await self.send_mail()
            case "increase_limit":
                txn = await self.increase_limit()
            case "transfer_to_okx":
                txn = await self.transfer()
            case "deploy":
                await self.account.deploy()
            case _:
                print(f"WRONG MODULE {module}")
        if txn:
            await exec(self, module, [txn])

        return 1


    async def transfer(self):
        super().__init__(
            address=ETH_ADDRESS,
            abi=TOKENS_ABI,
            provider=self.account
        )

        balance = await self.account.get_balance()
        balance_for_transfer = balance - uniform(*AMOUNT_TO_KEEP) * 1e18
        if balance_for_transfer < 0:
            return 0

        transfer = self.functions["transfer"].prepare(
            recipient=int(self.account._wallet["okx_addr"], 16),
            amount=int(balance_for_transfer)
        )

        return transfer


    async def send_mail(self):
        super().__init__(
            address=DMAIL_ADDRESS,
            abi=DMAIL_ABI,
            provider=self.account
        )

        send = self.functions["transaction"].prepare(
            to=self.generate_random_string(),
            theme=self.generate_random_string()
        )

        return send


    async def increase_limit(self):
        super().__init__(
            address=ETH_ADDRESS,
            abi=TOKENS_ABI,
            provider=self.account
        )

        increase = self.functions["increaseAllowance"].prepare(
            spender=choice([UNFRAMED_ADDRESS, FLEX_ADDRESS]),
            added_value=randint(1e13, 1e14)
        )

        return increase


    @staticmethod
    def generate_random_string() -> str:
        return ''.join(choice(hexdigits[:-6]) for _ in range(31))
