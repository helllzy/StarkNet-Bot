from asyncio import WindowsSelectorEventLoopPolicy, set_event_loop_policy, run
from inquirer.themes import load_theme_from_dict as loadth
from inquirer import List, prompt
from termcolor import colored

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.contract import Contract

from data.data import (
    TOKENS_ABI,
    ETH_ADDRESS,
    USDC_ADDRESS,
    USDT_ADDRESS,
    DAI_ADDRESS,
    ZKLEND_ETH_ADDRESS,
    WBTC_ADDRESS
)

TOKEN = {
    'ETH': ETH_ADDRESS,
    'USDC': USDC_ADDRESS,
    'USDT': USDT_ADDRESS,
    'DAI': DAI_ADDRESS,
    'ZK_ETH': ZKLEND_ETH_ADDRESS,
    'WBTC': WBTC_ADDRESS
}

# the first way
with open('data/addresses.txt') as file:
    addresses = [str(line.strip()) for line in file]

# OR the second way
# from account import CustomAccount
# KEYS = [key["private_key"] for key in WALLETS.values()]
# addresses = [hex(CustomAccount(key).address) for key in KEYS]


def get_coin():
    theme = {
        "Question": {
            "mark_color": "cyan"
        },
        "List": {
            "selection_color": "bold_green",
            "selection_cursor": ">>>",
            "unselected_color": "red"
        }
    }

    question = [
        List(
            'coin',
            message=colored("Choose the token", 'cyan'),
            choices=['ETH', 'USDC', 'USDT', 'DAI', 'ZK_ETH', 'WBTC'],
        )
    ]

    return prompt(questions=question, theme=loadth(theme))['coin']


async def main(address) -> str:
    while True:
        try:
            gateway_client = GatewayClient(net="mainnet")
            contract = Contract(address=coin_addr, abi=TOKENS_ABI, provider=gateway_client)

            result = await contract.functions["balanceOf"].call(int(address, 16))

            nonce = await gateway_client.get_contract_nonce(address)

            if coin in ('ETH', 'ZK_ETH'):
                balance = round(result.balance/1e18, 6)
            elif coin == 'WBTC':
                balance = round(result.balance/1e8, 6)
            else:
                balance = round(result.balance/1e6, 6)

            return f'{address};{nonce};{balance}'

        except:
            pass


if __name__ == '__main__':
    coin = get_coin()
    coin_addr = TOKEN[coin]

    with open('data/balance&nonce.txt', 'w') as file:

        for num, address in enumerate(addresses, start=1):
            set_event_loop_policy(WindowsSelectorEventLoopPolicy())

            info = run(main(address))
            print(num, info.replace(';', ' | '), coin, sep=' | ')

            file.write(f"{info}\n")
