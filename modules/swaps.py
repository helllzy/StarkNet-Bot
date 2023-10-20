from random import randint, uniform, choice
from time import time
from aiohttp import ClientError, ClientSession
from fake_useragent import UserAgent

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.contract import Contract

from config import SWAP_PERCENTAGES
from modules.utils import (
    exec,
    prepare_token,
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
    STARKEX_ADDRESS,
    STARKEX_ABI,
    JEDI_ADDRESS,
    JEDI_ABI,
    K10_ADDRESS,
    K10_ABI,
    MYSWAP_ADDRESS,
    MYSWAP_ABI,
    SITH_ADDRESS,
    SITH_ABI,
    AVNU_ADDRESS,
    AVNU_ABI,
    FIBROUS_ADDRESS,
    FIBROUS_ABI,
    Module
)


class Swap(Contract, Module):
    def __init__(self, account):
        self.account = account


    async def start(self, module, liquidity=None) -> int:
        if not liquidity:
            for token in [USDT_ADDRESS, USDC_ADDRESS, DAI_ADDRESS, WBTC_ADDRESS]:
                await sleeping([3, 5])

                balance = await self.account.get_balance(token)

                if token != WBTC_ADDRESS and balance/1e5 > 5: # 0.5$
                    break

                if token == WBTC_ADDRESS and balance/1e2 > 12: # 0.35$
                    break

                token = None

            if not token:
                self.token1, self.token2 = ETH_ADDRESS, prepare_token()
                self.balance_for_swap = int(
                    (await self.account.get_balance(
                        self.token1)) * randint(*SWAP_PERCENTAGES) / 100)
            else:
                self.token1, self.token2 = token, ETH_ADDRESS
                self.balance_for_swap = int(balance)
        else:
            self.token1, self.token2 = ETH_ADDRESS, prepare_token()
            self.balance_for_swap = int(uniform(1.3, 2) * 1e14) # 0.2$ - 0.3$

        match module:

            case "jedi_swap":
                swap = await self.jedi()

            case "10k_swap":
                swap = await self.k10()

            case "myswap":
                swap = await self.myswap()

            case "sith_swap":
                swap = await self.sith()

            case "avnu_swap":
                swap = await self.avnu()

            case "starkex_swap":
                swap = await self.starkex()

            case "fibrous_swap":
                swap = await self.fibrous()

            case _:
                print(f"WRONG MODULE {module}")

        appr = await approve(self.token1, self.account, self.address, self.balance_for_swap)

        await exec(self, module, [appr, swap])

        if liquidity:
            return self.token2

        return 1


    async def starkex(self):
        super().__init__(
            address=STARKEX_ADDRESS,
            abi=STARKEX_ABI,
            provider=self.account
        )

        path = [self.token1, self.token2]
        
        amount_out_min = await self.functions['getAmountsOut'].call(
            amountIn=self.balance_for_swap,
            path=path
        )

        swap = self.functions['swapExactTokensForTokens'].prepare(
            amountIn=self.balance_for_swap,
            amountOutMin=use_slippage(amount_out_min.amounts[1], 2),
            path=path,
            to=self.account.address,
            deadline=int(time() + 3600)
        )

        return swap


    async def jedi(self):
        super().__init__(
            address=JEDI_ADDRESS,
            abi=JEDI_ABI,
            provider=self.account
        )

        path = [self.token1, self.token2]

        amount_out_min = await self.functions['get_amounts_out'].call(
            amountIn=self.balance_for_swap,
            path=path
        )

        swap = self.functions['swap_exact_tokens_for_tokens'].prepare(
            amountIn=self.balance_for_swap,
            amountOutMin=use_slippage(amount_out_min.amounts[1], 2),
            path=path,
            to=self.account.address,
            deadline=int(time() + 3600)
        )

        return swap


    async def sith(self):
        super().__init__(
            address=SITH_ADDRESS,
            abi=SITH_ABI,
            provider=self.account
        )

        routes = [{
            'from_address': self.token1,
            'to_address': self.token2,
            'stable': 0
        }]

        amount_out_min = await self.functions['getAmountsOut'].call(
            amount_in=self.balance_for_swap,
            routes=routes
        )

        swap = self.functions['swapExactTokensForTokensSupportingFeeOnTransferTokens'].prepare(
            amount_in=self.balance_for_swap,
            amount_out_min=use_slippage(amount_out_min.amounts[1], 2),
            routes=routes,
            to=self.account.address,
            deadline=int(time() + 3600)
        )

        return swap
    

    async def myswap(self):
        super().__init__(
            address=MYSWAP_ADDRESS,
            abi=MYSWAP_ABI,
            provider=self.account
        )
        
        pools_data = {
            "USDC": 1, "USDT": 4, "DAI": 2
        }

        if self.token1 == WBTC_ADDRESS:
            self.token1 = choice([USDC_ADDRESS, USDT_ADDRESS, DAI_ADDRESS])
        elif self.token2 == WBTC_ADDRESS:
            self.token2 = choice([USDC_ADDRESS, USDT_ADDRESS, DAI_ADDRESS])

        opposite = False

        if self.token1 == ETH_ADDRESS:

            if self.token2 == USDC_ADDRESS:
                pool_id = pools_data["USDC"]
            elif self.token2 == USDT_ADDRESS:
                pool_id = pools_data["USDT"]
            else:
                pool_id = pools_data["DAI"]
                opposite = True
        else:
            if self.token1 == DAI_ADDRESS:
                pool_id = pools_data["DAI"]
            else:
                opposite = True

                if self.token1 == USDC_ADDRESS:
                    pool_id = pools_data["USDC"]
                elif self.token1 == USDT_ADDRESS:
                    pool_id = pools_data["USDT"]

        pool_data = await self.functions["get_pool"].prepare(
            pool_id=pool_id
        ).call()

        pool_data = pool_data.pool
        reserveA = pool_data.get('token_a_reserves')
        reserveB = pool_data.get('token_b_reserves')

        if opposite:
            reserveA, reserveB = reserveB, reserveA

        amount_out_min = reserveB * self.balance_for_swap / reserveA

        swap = self.functions['swap'].prepare(
            pool_id=pool_id,
            token_from_addr=self.token1,
            amount_from=self.balance_for_swap,
            amount_to_min=use_slippage(amount_out_min, 2)
        )

        return swap


    async def k10(self):
        super().__init__(
            address=K10_ADDRESS,
            abi=K10_ABI,
            provider=self.account
        )

        path = [self.token1, self.token2]

        amount_out_min = await self.functions['getAmountsOut'].call(
            path=path,
            amountIn=self.balance_for_swap
        )

        swap = self.functions['swapExactTokensForTokens'].prepare(
            amountIn=self.balance_for_swap,
            amountOutMin=use_slippage(amount_out_min.amounts[1], 2),
            path=path,
            to=self.account.address,
            deadline=int(time() + 3600)
        )

        return swap


    async def avnu(self):
        super().__init__(
            address=AVNU_ADDRESS,
            abi=AVNU_ABI,
            provider=self.account,
            cairo_version=1
        )

        swap_data = await self.avnu_get_swap_data(
            hex(self.token1), hex(self.token2), hex(self.balance_for_swap))
        
        swap = self.functions['multi_route_swap'].prepare(**swap_data)

        return swap


    async def fibrous(self):
        super().__init__(
            address=FIBROUS_ADDRESS,
            abi=FIBROUS_ABI,
            provider=self.account,
            cairo_version=1
        )

        swap_parameters = await self.fibrous_get_swap_data(
            hex(self.token1), hex(self.token2), hex(self.balance_for_swap))
        
        swap = Call(
            to_addr=self.address,
            selector=get_selector_from_name('swap'),
            calldata=swap_parameters
        )

        return swap


    async def fibrous_get_swap_data(
        self, sell_token_address, buy_token_address, sell_amount) -> dict:
        ua = UserAgent(os=["windows"], browsers=['chrome'])
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://app.fibrous.finance',
            'Referer': 'https://app.fibrous.finance/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': ua.random,
        }

        params = {
            'amount': sell_amount,
            'tokenInAddress': sell_token_address,
            'tokenOutAddress': buy_token_address,
            'slippage': 0.02,
            'destination': hex(self.account.address)
        }

        async with ClientSession(headers=headers) as session:
                async with session.get(
                      'https://api.fibrous.finance/execute', params=params) as response:

                    if response.status == 200:
                        data = await response.json()
                        swap_parameters = []

                        for value in data:
                            if isinstance(value, str):
                                if value.startswith('0x'):
                                    swap_parameters.append(int(value, 16))
                                else:
                                    swap_parameters.append(int(value))
                            else:
                                swap_parameters.append(value)

                        return swap_parameters
                    else:
                        raise ClientError(f'Response status {response.status}!')


    async def avnu_get_swap_data(
        self, sell_token_address, buy_token_address, sell_amount) -> dict:
        ua = UserAgent(os=["windows"], browsers=['chrome'])
        headers = {
            'authority': 'starknet.api.avnu.fi',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://app.avnu.fi',
            'referer': 'https://app.avnu.fi/',
            'sec-ch-ua': '"Windows"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Not A;Brand";v="99", "Chromium";v="111", "Google Chrome";v="111""',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': ua.random,
        }

        params = {
            'sellTokenAddress': sell_token_address,
            'buyTokenAddress': buy_token_address,
            'sellAmount': sell_amount,
            'takerAddress': hex(self.account.address),
            'size': '3',
            'integratorName': 'AVNU Portal',
        }

        async with ClientSession(headers=headers) as session:
                async with session.get(
                    'https://starknet.api.avnu.fi/swap/v1/quotes', params=params) as response:

                    if response.status == 200:
                        data = await response.json()
                        json_data = {
                            'quoteId': data[0]['quoteId'],
                            'takerAddress':hex(self.account.address),
                            'slippage': 0.02,
                        }
                    else:
                        raise ClientError(f'Response status {response.status}!')

                async with session.post('https://starknet.api.avnu.fi/swap/v1/build', json=json_data) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        call_data = None

                        for k, v in data.items():
                            if k == 'calldata':
                                call_data = v

                        swap_data = {
                            'token_from_address': int(call_data[0], 16),
                            'token_from_amount': int(call_data[1], 16),
                            'token_to_address': int(call_data[3], 16),
                            'token_to_amount': int(call_data[4], 16),
                            'token_to_min_amount': int(call_data[6], 16),
                            'beneficiary': int(call_data[8], 16),
                            'integrator_fee_amount_bps': int(call_data[9], 16),
                            'integrator_fee_recipient': int(call_data[10], 16),
                            'routes': [
                                {
                                    'token_from': int(call_data[12], 16),
                                    'token_to': int(call_data[13], 16),
                                    'exchange_address': int(call_data[14], 16),
                                    'percent': int(call_data[15], 16),
                                    'additional_swap_params': [int(call_data[16], 16)]
                                }
                            ]
                        }

                        return swap_data
                    raise ClientError(f'Response status {response.status}!')
        