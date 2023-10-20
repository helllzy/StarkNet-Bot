from sys import platform
from asyncio import WindowsSelectorEventLoopPolicy, set_event_loop_policy, run
from random import shuffle, sample, randint, choice
from termcolor import cprint

from starknet_py.net.gateway_client import GatewayClient

from modules.account import CustomAccount, Account
from modules.transactions import Transaction
from modules.liquidity import Liquidity
from data.data import WALLETS, HELZY
from modules.markets import Market
from modules.zklend import ZkLend
from modules.swaps import Swap
from modules.mints import Mint
from modules.okx import OKX
from config import (
    RANDOMIZE_WALLETS,
    USE_PROXY,
    DELAY,
    RANDOMIZE_MODULES,
    MOD_DELAY,
    SKIP_MODS,
    MODS_COUNT,
    MODULES,
    ZK_VOLUME,
    TRANSFER_TO_OKX,
    WITHDRAW_FROM_OKX,
    ZK_REPEATS,
    DEPLOY_WALLETS,
    EXACT_NONCE,
    EXACT_NONCE_COUNT
)
from modules.utils import (
    sleeping,
    logger,
    check_gas,
    info,
    check_balance,
    result_data,
    send_message
)


ACTION = {
    **dict.fromkeys(['starkverse', 'starknet_id'], Mint),
    **dict.fromkeys(['jedi_swap', '10k_swap', 'myswap', 'sith_swap', \
                     'avnu_swap', 'starkex_swap', 'fibrous_swap'], Swap),
    **dict.fromkeys(['jedi_liquidity', '10k_liquidity', 'sith_liquidity'], Liquidity),
    **dict.fromkeys(['flex_market', 'unframed_market'], Market),
    **dict.fromkeys(['dmail', 'increase_limit', 'transfer_to_okx', 'deploy'], Transaction),
    **dict.fromkeys(['zk_lending', 'collateral'], ZkLend),
    'withdraw_from_okx': OKX
}


async def main():
    if RANDOMIZE_WALLETS:
        shuffle(KEYS)

    for key_id, private in enumerate(KEYS, start=1):
        try:
            account = CustomAccount(private)
        except:
            logger.critical(key_id, 'PROXY ERROR', sep=" | ")
            continue

        try:
            logger.debug(f"| Working on {key_id} wallet: {hex(account.address)}")
            await wallet_proceeding(account, key_id)
        except Exception as error:
            logger.critical(f"AN ERROR WHILE WALLET PROCEEDING {str(error)}")

        try:
            global accs_result
            if key_id < len(KEYS):
                await sleeping(DELAY, "| Sleeping between wallets", "cyan")
                print()

                if key_id % 10 == 0:
                    await send_message(accs_result)
                    accs_result = {}
            else:
                await send_message(accs_result)
                logger.success('| All wallets processed')
        except Exception as error:
            logger.critical(f"AN ERROR WHILE SENDING TG MESSAGE {str(error)}")

        if USE_PROXY:
            await account.custom_session.close()


async def wallet_proceeding(account: Account, key_id) -> None:
    ALL_MODULES = MODULES
    if EXACT_NONCE:
        gateway_client = GatewayClient(net="mainnet")

        nonce = await gateway_client.get_contract_nonce(account.address)
        trans_count = randint(*EXACT_NONCE_COUNT)-nonce
        if trans_count > 0:
            ALL_MODULES = sample(MODULES*1000, trans_count)
        else:
            return

    else:

        if RANDOMIZE_MODULES:
            shuffle(ALL_MODULES)

        if SKIP_MODS:
            ALL_MODULES = sample(MODULES, randint(*MODS_COUNT))

        if ZK_VOLUME:
            [ALL_MODULES.insert(-1, "zk_lending") for _ in range(randint(*ZK_REPEATS))]

        if TRANSFER_TO_OKX:
            ALL_MODULES.insert(-1, "transfer_to_okx")

        if DEPLOY_WALLETS:
            ALL_MODULES.insert(0, "deploy")

        if WITHDRAW_FROM_OKX:
            ALL_MODULES.insert(0, "withdraw_from_okx")
        else:
            balance = await check_balance(account)
            
            if not balance:
                return
            elif 'swap' in balance or balance == 'zk_lending':
                ALL_MODULES.insert(0, balance)

    info(f"Actual modules: {ALL_MODULES}")
    for module_id, module in enumerate(ALL_MODULES, start=1):
        await module_proceeding(account, module)

        if module_id < len(ALL_MODULES):
            await sleeping(MOD_DELAY, "| Sleeping between modules", "yellow")

    if not balance or not isinstance(balance, int):
        balance = await account.get_balance()

    accs_result[str(hex(account.address))] = {
        "id": str(key_id),
        "mods": ALL_MODULES,
        "fee": await result_data(account, balance)
    }


@check_gas
async def module_proceeding(account: Account, module, retry=0):
    while retry < 5:
        retry += 1

        try:
            result = await ACTION[module](account).start(module)

            if result == 1:
                return
        except Exception as e:
            logger.error(f"{hex(account.address)} | {module} | {str(e)}")
        await sleeping([60, 120])


if __name__ == '__main__':
    cprint(choice(HELZY), choice(['green', 'magenta', 'light_cyan']))

    KEYS, accs_result = [key["private_key"] for key in WALLETS.values()], {}

    if platform.startswith("win"):
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    run(main())
