from decimal import Decimal, ROUND_HALF_UP
from random import randint, choice
from functools import wraps
from asyncio import sleep
from requests import post
from loguru import logger
from web3 import Web3

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.contract import Contract

from data.data import (
    EMOJI_NUMBERS,
    TOKENS_ABI,
    USDT_ADDRESS,
    USDC_ADDRESS,
    DAI_ADDRESS,
    ZKLEND_ETH_ADDRESS,
    WBTC_ADDRESS
)
from config import (
    MAX_GWEI,
    ALLOWED_TOKENS,
    BOT_TOKEN, CHAT_ID,
    CURRENT_ETH_PRICE
)

logger.add('data/logs.log')


async def result_data(account, balance) -> int:
    while True:

        try:
           return (balance - (await account.get_balance())) / 1e18

        except:
            await sleep(5)


async def approve(contract_address, account, spender, amount):
    contract = Contract(
            address=contract_address,
            abi=TOKENS_ABI,
            provider=account
        )

    approve = contract.functions['approve'].prepare(
            spender=spender,
            amount=amount
        )

    return approve


async def check_balance(account, retry=0) -> str | int | None:
    while retry<5:
        retry += 1
        try:
            for token in [None, USDT_ADDRESS, USDC_ADDRESS, \
                          DAI_ADDRESS, ZKLEND_ETH_ADDRESS, WBTC_ADDRESS]:

                balance = await account.get_balance(token)

                if not token and balance/1e14 > 5: # 0.8$
                    return balance

                elif not token and balance/1e14 < 5: # 0.8$
                    await send_message(f"{hex(account.address)} has insufficient balance:"
                                       f"{round(balance/1e18, 5)}")
                    logger.error(f"{hex(account.address)} has insufficient balance "
                                 f"{round(balance/1e18, 5)}")
                    return

                elif token == ZKLEND_ETH_ADDRESS and balance/1e14 > 3: # 0.5$
                    return "zklend_supply"

                elif token == WBTC_ADDRESS and balance/1e2 > 12 or token and balance/1e5 > 5: # 0.5$
                    return choice(["jedi_swap", "10k_swap", "sith_swap"])

                await sleep(3)
        except:
            logger.error('Got an error while checking balance, trying again in 10 secs')
            await sleep(10)
        
    return


async def send_message(text) -> None:
    if isinstance(text, dict):
        message = ''
        for addr in list(text.keys()):
            message += f'{add_emoji(text[addr]["id"])} | {addr[:4]}...{addr[-4:]}' \
                       f'| FEE: {round(text[addr]["fee"]*CURRENT_ETH_PRICE, 2)}$' \
                       f'| {"; ".join(text[addr]["mods"])}\n'

        text = message.strip()
    post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id="
        f"{CHAT_ID}&text={text}"
        )


def add_emoji(text) -> str:
    return ''.join([EMOJI_NUMBERS[num] for num in text])


async def exec(self, module, calls) -> None:
    module = module.capitalize()

    tx_response = await self.account.execute(calls=calls, auto_estimate=True)
    info(
        f"| {module} | Waiting transaction: "
        f"https://starkscan.co/tx/{hex(tx_response.transaction_hash)}", "magenta"
        )

    await self.account.client.wait_for_tx(tx_response.transaction_hash)
    logger.success(f"| {module} | Transaction accepted")


async def sleeping(secs, text=None, color=None) -> None:
    if text:
        info(text, color)

    await sleep(randint(*secs))


def info(text, color="white") -> None:
    logger.opt(colors=True).info(f'<{color}>{text}</{color}>')


def check_gas(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        gateway_client = GatewayClient(net="mainnet")

        while True:
            try:
                w3 = Web3(Web3.HTTPProvider(choice(
                    ['https://rpc.ankr.com/eth', 'https://1rpc.io/eth'])))
                block = await gateway_client.get_block(block_number='pending')
                stark_gas_price = round(block.gas_price / 10 ** 9, 2)
                eth_gas_price = round(w3.from_wei(w3.eth.gas_price, 'gwei'), 2)

                if stark_gas_price > MAX_GWEI or eth_gas_price > MAX_GWEI:
                    logger.warning(
                        f"STARK gas`s {stark_gas_price} | "
                        f"ETH gas`s {eth_gas_price} | sleep 30 seconds"
                        )
                    await sleep(30)
                else:
                    break

            except:
                pass

        return await func(*args, **kwargs)
    return wrapper


def use_slippage(v, slippage) -> int:
        slippage_values = {
            0.1: lambda x: (x / 1000) * 999,
            0.5: lambda x: (x / 1000) * 995,
            1: lambda x: (x / 1000) * 990,
            2: lambda x: (x / 1000) * 980,
        }

        v = Decimal(v)
        slippage_fn = slippage_values.get(slippage, lambda x: x)

        result = slippage_fn(v).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        return int(result)


def prepare_token() -> int:
    match choice(ALLOWED_TOKENS):

        case 'USDT':
            token = USDT_ADDRESS

        case 'USDC':
            token = USDC_ADDRESS

        case 'DAI':
            token = DAI_ADDRESS

        case 'WBTC':
            token = WBTC_ADDRESS

        case _:
            logger.critical("WRONG TOKEN, CHECK ALLOWED TOKENS!")

    return token
