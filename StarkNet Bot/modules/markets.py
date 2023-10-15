from string import hexdigits
from random import choice

from starknet_py.contract import Contract

from modules.utils import exec, sleeping
from data.data import (
    UNFRAMED_ADDRESS,
    UNFRAMED_ABI,
    FLEX_ABI,
    FLEX_ADDRESS,
    STARKVERSE_ADDRESS,
    STARKVERSE_ABI,
    STARK_ID_ADDRESS,
    STARK_ID_ABI,
    Module
)


class Market(Contract, Module):
    def __init__(self, account):
        self.account = account


    async def start(self, module) -> int:
        await self.approve(module)
        await sleeping([60, 120])

        match module:
            case "flex_market":
                cancel = await self.flex()
            case "unframed_market":
                cancel = await self.unframed()
            case _:
                print(f"WRONG MODULE {module}")

        await exec(self, module, [cancel])
        return 1


    async def approve(self, market) -> None:
        match market:
            case "flex_market":
                operator = FLEX_ADDRESS
            case "unframed_market":
                operator = UNFRAMED_ADDRESS
            case _:
                print(f"WRONG MARKET {market}")

        nft = choice(
            [{"address": STARK_ID_ADDRESS, "abi": STARK_ID_ABI, "name": 1},
             {"address": STARKVERSE_ADDRESS, "abi": STARKVERSE_ABI, "name": 0}]
             )

        nft_contract = Contract(
            address=nft["address"],
            abi=nft["abi"],
            provider=self.account
        )

        is_approved = await nft_contract.functions['isApprovedForAll'].call(
            owner=self.account.address, operator=operator)
        if nft["address"] == STARKVERSE_ADDRESS and is_approved.approved == 1:
            return
        if nft["address"] == STARK_ID_ADDRESS and is_approved.is_approved == 1:
            return

        approve = nft_contract.functions['setApprovalForAll'].prepare(
            operator=operator,
            approved=1
        )

        await exec(self, "approve", [approve])


    async def flex(self):
        super().__init__(
            address=FLEX_ADDRESS,
            abi=FLEX_ABI,
            provider=self.account
        )

        cancel = self.functions['cancelMakerOrder'].prepare(
            orderNonce=20
        )

        return cancel


    async def unframed(self):
        super().__init__(
            address=UNFRAMED_ADDRESS,
            abi=UNFRAMED_ABI,
            provider=self.account,
            cairo_version=1
        )

        cancel = self.functions['cancel_orders'].prepare(
            order_nonces=self.generate_random_nonce()
        )

        return cancel


    @staticmethod
    def generate_random_nonce() -> str:
        return '0x' + ''.join(choice(hexdigits[:-6]) for _ in range(63))
