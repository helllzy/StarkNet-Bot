from random import randint

from starknet_py.contract import Contract

from modules.utils import exec
from data.data import (
    STARK_ID_ADDRESS,
    STARK_ID_ABI,
    STARKVERSE_ADDRESS,
    STARKVERSE_ABI,
    Module
)


class Mint(Contract, Module):
    def __init__(self, account):
        self.account = account


    async def start(self, module) -> int:
        match module:
            case "starknet_id":
                calls = await self.mint_identities()
            case "starkverse":
                calls = await self.starkverse()
            case _:
                print(f"WRONG MODULE {module}")

        await exec(self, module, [calls])

        return 1


    async def starkverse(self):
        super().__init__(
            address=STARKVERSE_ADDRESS,
            abi=STARKVERSE_ABI,
            provider=self.account
        )

        return self.functions["publicMint"].prepare(to=self.account.address)


    async def mint_identities(self):
        super().__init__(
            address=STARK_ID_ADDRESS,
            abi=STARK_ID_ABI,
            provider=self.account
        )

        return self.functions["mint"].prepare(randint(400000, 20000000))
