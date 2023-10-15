from random import uniform
from time import time

from starknet_py.contract import Contract

from modules.swaps import Swap
from modules.utils import (
    exec,
    sleeping,
    approve,
    use_slippage
)
from data.data import (
    USDT_ADDRESS,
    USDC_ADDRESS,
    DAI_ADDRESS,
    WBTC_ADDRESS,
    ETH_ADDRESS,
    JEDI_ABI,
    JEDI_ADDRESS,
    SITH_ABI,
    SITH_ADDRESS,
    K10_ABI,
    K10_L_ABI,
    K10_ADDRESS,
    K10_LIQUIDITY_ADDRESS,
    K10_L_TOKEN_ABI,
    Module
)


class Liquidity(Contract, Module):
    def __init__(self, account):
        self.account = account
        self.token1_for_liquidity = int(uniform(7.5, 25) * 1e12) # 0.01 - 0.04
        self.token1 = ETH_ADDRESS


    async def start(self, module, token2=None) -> int:
        for token in [USDT_ADDRESS, USDC_ADDRESS, DAI_ADDRESS, WBTC_ADDRESS]:
            await sleeping([3, 5])

            balance = await self.account.get_balance(token)

            if token != WBTC_ADDRESS and balance/1e5 > 1: # 0.1$
                token2 = token
                self.token2_for_liquidity = int(uniform(0.1, 0.4) * 1e5) # 0.01 - 0.04
                break

            elif token == WBTC_ADDRESS and balance/10 > 35: # 0.1$
                token2 = token
                self.token2_for_liquidity = int(uniform(5, 15) * 10) # 0.01 - 0.04
                break

        if not token2:
            self.token2 = await Swap(self.account).start(
                module.replace('liquidity', 'swap'), liquidity=True)
            await sleeping([60, 120])

            if self.token2 == ETH_ADDRESS:
                return

            elif self.token2 != WBTC_ADDRESS:
                self.token2_for_liquidity = int(uniform(0.1, 0.4) * 1e5) # 0.01 - 0.04

            elif self.token2 == WBTC_ADDRESS:
                self.token2_for_liquidity = int(uniform(5, 15) * 10) # 0.01 - 0.04
        else:
            self.token2 = token2

        match module:
            case "jedi_liquidity":
                liquidity = await self.jedi()
            case "10k_liquidity":
                liquidity = await self.k10()
            case "sith_liquidity":
                liquidity = await self.sith()
            case _:
                print(f"WRONG MODULE {module}")
                return 1

        appr1 = await approve(self.token1, self.account, self.address, self.token1_for_liquidity)
        appr2 = await approve(self.token2, self.account, self.address, self.token2_for_liquidity)

        await exec(self, module, [appr1, appr2, liquidity])

        return 1


    async def jedi(self):
        super().__init__(
            address=JEDI_ADDRESS,
            abi=JEDI_ABI,
            provider=self.account
        )

        tokens = await self.functions['sort_tokens'].call(
            tokenA=self.token1,
            tokenB=self.token2
        )

        self.token1, self.token2, path = tokens[0], tokens[1], [tokens[0], tokens[1]]

        if self.token1 != ETH_ADDRESS:
            self.token1_for_liquidity = self.token2_for_liquidity

        amount_out_min = await self.functions['get_amounts_out'].call(
            amountIn=self.token1_for_liquidity,
            path=path
        )

        self.token1_for_liquidity = amount_out_min.amounts[0]
        self.token2_for_liquidity = amount_out_min.amounts[1]

        liquidity = self.functions['add_liquidity'].prepare(
            tokenA=self.token1,
            tokenB=self.token2,
            amountADesired=self.token1_for_liquidity,
            amountBDesired=self.token2_for_liquidity,
            amountAMin=use_slippage(self.token1_for_liquidity, 2),
            amountBMin=use_slippage(self.token2_for_liquidity, 2),
            to=self.account.address,
            deadline=int(time() + 3600)
        )

        return liquidity


    async def sith(self):
        super().__init__(
            address=SITH_ADDRESS,
            abi=SITH_ABI,
            provider=self.account
        )

        tokens = await self.functions['sortTokens'].call(
            token_a=self.token1,
            token_b=self.token2
        )

        self.token1, self.token2 = tokens[0], tokens[1]

        if self.token1 != ETH_ADDRESS:
            self.token1_for_liquidity = self.token2_for_liquidity

        routes = [{
            'from_address': self.token1,
            'to_address': self.token2,
            'stable': 0
        }]

        amount_out_min = await self.functions['getAmountsOut'].call(
            amount_in=self.token1_for_liquidity,
            routes=routes
        )

        self.token1_for_liquidity = amount_out_min.amounts[0]
        self.token2_for_liquidity = amount_out_min.amounts[1]

        liquidity = self.functions['addLiquidity'].prepare(
            token_a=self.token1,
            token_b=self.token2,
            stable=0,
            amount_a_desired=self.token1_for_liquidity,
            amount_b_desired=self.token2_for_liquidity,
            amount_a_min=use_slippage(self.token1_for_liquidity, 2),
            amount_b_min=use_slippage(self.token2_for_liquidity, 2),
            to=self.account.address,
            deadline=int(time() + 3600)
        )

        return liquidity


    async def k10(self):
        super().__init__(
            address=K10_ADDRESS,
            abi=K10_ABI,
            provider=self.account
        )

        contract = Contract(
            address=K10_LIQUIDITY_ADDRESS, abi=K10_L_ABI, provider=self.account
        )

        token = await contract.functions['getPair'].call(
            token0=self.token1,
            token1=self.token2
        )

        lp_pair = Contract(
            address=token.pair, abi=K10_L_TOKEN_ABI, provider=self.account
        )

        token1 = await lp_pair.functions['token0'].call()

        if token1 != self.token1:
            self.token1, self.token2 = self.token2, self.token1
            self.token1_for_liquidity = self.token2_for_liquidity

        amount_out_min = await self.functions['getAmountsOut'].call(
            amountIn=self.token1_for_liquidity,
            path=[self.token1, self.token2],
        )

        self.token1_for_liquidity = amount_out_min.amounts[0]
        self.token2_for_liquidity = amount_out_min.amounts[1]

        liquidity = self.functions['addLiquidity'].prepare(
            tokenA=self.token1,
            tokenB=self.token2,
            amountADesired=self.token1_for_liquidity,
            amountBDesired=self.token2_for_liquidity,
            amountAMin=use_slippage(self.token1_for_liquidity, 2),
            amountBMin=use_slippage(self.token2_for_liquidity, 2),
            to=self.account.address,
            deadline=int(time() + 3600),
        )

        return liquidity
