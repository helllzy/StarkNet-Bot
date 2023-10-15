from random import randint

from starknet_py.contract import Contract

from config import LENDING_PERCENTAGES
from modules.utils import (
    exec,
    prepare_token,
    sleeping,
    approve
)
from data.data import (
    ZKLEND_ABI,
    ZKLEND_ADDRESS,
    ETH_ADDRESS,
    ZKLEND_ETH_ADDRESS,
    Module
)


class ZkLend(Contract, Module):

    def __init__(self, account):
        super().__init__(
            address=ZKLEND_ADDRESS,
            abi=ZKLEND_ABI,
            provider=account
        )


    async def start(self, module) -> int:

        self.zk_balance = await self.account.get_balance(ZKLEND_ETH_ADDRESS)

        if self.zk_balance > 5 * 1e14:
            module = "withdraw"

        match module:
            case "withdraw":
                await self.withdraw()
            case "zk_lending":
                await self.lending()
            case "collateral":
                await self.collateral()
            case _:
                print(f"WRONG MODULE {module}")

        return 1


    async def collateral(self, token=prepare_token()) -> None:
        if await self.is_enabled(token) == 1:
            await self.disable(token)
        else:
            await exec(self, "enable", [await self.enable(token)])
            await sleeping([60, 120])
            await self.collateral(token)


    async def lending(self) -> None:
        balance = await self.account.get_balance()
        balance_for_lending = int(balance * randint(*LENDING_PERCENTAGES) / 100)

        appr = await approve(ETH_ADDRESS, self.account, self.address, balance_for_lending)

        deposit = self.functions['deposit'].prepare(
            token=ETH_ADDRESS,
            amount=balance_for_lending,
        )

        calls = [appr, deposit]

        if await self.is_enabled() == 1:

            if randint(1, 3) == 1:
                await self.disable()

                await sleeping([60, 120])

                enable_collateral = await self.enable(ETH_ADDRESS)
                calls.append(enable_collateral)

        await exec(self, "lending", calls)

        await sleeping([60, 120])

        await self.start("withdraw")


    async def withdraw(self) -> None:
        withdraw = self.functions['withdraw'].prepare(
            token=ETH_ADDRESS,
            amount=self.zk_balance-randint(12500000000000, 25000000000000)
        )

        await exec(self, "withdraw", [withdraw])


    async def is_enabled(self, token=ETH_ADDRESS) -> int:
        is_enabled = await self.functions['is_collateral_enabled'].call(
            user=self.account.address, token=token)
        return is_enabled.enabled


    async def enable(self, token=ETH_ADDRESS):
        return self.functions['enable_collateral'].prepare(token=token)


    async def disable(self, token=ETH_ADDRESS) -> None:
        await exec(self, "disable", [self.functions['disable_collateral'].prepare(token=token)])
