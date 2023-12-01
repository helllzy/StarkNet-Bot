from config import USE_PROXY, TRANSFER_TO_OKX, WITHDRAW_FROM_OKX, CHANGED_KEY

from abc import ABC, abstractmethod
from loguru import logger
from json import load

with open('data/priv.txt') as file:
    KEYS = [x.strip() for x in file.readlines()]

if len(KEYS) < 1:
        logger.critical("You didn`t add wallets in priv.txt!")
        exit()

WALLETS = {}
for _id in range(len(KEYS)):
    WALLETS[f'w{_id}'] = {"private_key": KEYS[_id]}

    if USE_PROXY:
        with open('data/proxies.txt') as file:
            PROXIES = [x.strip() for x in file.readlines()]

        if len(KEYS) > len(PROXIES):
            logger.critical('Number of wallets isn`t equal to number of proxies')
            exit()

        WALLETS[f'w{_id}']["proxy"] = PROXIES[_id]

    if WITHDRAW_FROM_OKX or CHANGED_KEY:
        with open('data/addresses.txt') as file:
            ADDRESSES = [line.strip() for line in file]
        WALLETS[f'w{_id}']["address"] = ADDRESSES[_id]

    if TRANSFER_TO_OKX:
        with open('data/okx_addresses.txt') as file:
            OKX_ADDRESSES = [line.strip() for line in file]
        WALLETS[f'w{_id}']["okx_addr"] = OKX_ADDRESSES[_id]

with open('data/abis/dmail.json') as file:
    DMAIL_ABI = load(file)

with open('data/abis/jedi_swap.json') as file:
    JEDI_ABI = load(file)

with open('data/abis/token.json') as file:
    TOKENS_ABI = load(file)

with open('data/abis/starknet_id.json') as file:
    STARK_ID_ABI = load(file)

with open('data/abis/zklend.json') as file:
    ZKLEND_ABI = load(file)

with open('data/abis/ten_k_swap.json') as file:
    K10_ABI = load(file)

with open('data/abis/myswap.json') as file:
    MYSWAP_ABI = load(file)

with open('data/abis/ten_k_liquidity.json') as file:
    K10_L_ABI = load(file)

with open('data/abis/ten_k_liquidity_token.json') as file:
    K10_L_TOKEN_ABI = load(file)

with open('data/abis/starkverse.json') as file:
    STARKVERSE_ABI = load(file)

with open('data/abis/sith_swap.json') as file:
    SITH_ABI = load(file)

with open('data/abis/avnu.json') as file:
    AVNU_ABI = load(file)

with open('data/abis/starkex.json') as file:
    STARKEX_ABI = load(file)

with open('data/abis/unframed.json') as file:
    UNFRAMED_ABI = load(file)

with open('data/abis/flex.json') as file:
    FLEX_ABI = load(file)

with open('data/abis/fibrous.json') as file:
    FIBROUS_ABI = load(file)


class Module(ABC):
    def __init__(self, account) -> None:
        self.account = account

    
    @abstractmethod
    async def start() -> None:
        pass


WBTC_ADDRESS=0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac
ETH_ADDRESS=0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
USDT_ADDRESS=0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8
DAI_ADDRESS=0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3
USDC_ADDRESS=0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8
JEDI_ADDRESS=0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023
DMAIL_ADDRESS=0x0454F0BD015E730E5ADBB4F080B075FDBF55654FF41EE336203AA2E1AC4D4309
STARK_ID_ADDRESS=0x05DBDEDC203E92749E2E746E2D40A768D966BD243DF04A6B712E222BC040A9AF
ARGENT_PROXY_CLASS_HASH=0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
ARGENT_IMPLEMENTATION_CLASS_HASH=0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2
SELECTOR=0x79dc0da7c54b95f10aa182ad0a46400db63156920adb65eca2654c0945a463
STARKVERSE_ADDRESS=0x060582df2cd4ad2c988b11fdede5c43f56a432e895df255ccd1af129160044b8
K10_ADDRESS=0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1
K10_LIQUIDITY_ADDRESS=0x01c0a36e26a8f822e0d81f20a5a562b16a8f8a3dfd99801367dd2aea8f1a87a2
SITH_ADDRESS=0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627
MYSWAP_ADDRESS=0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28
ZKLEND_ADDRESS=0x04c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05
ZKLEND_ETH_ADDRESS=0x01b5bd713e72fdc5d63ffd83762f81297f6175a5e0a4771cdadbc1dd5fe72cb1
AVNU_ADDRESS=0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f
STARKEX_ADDRESS=0x07ebd0e95dfc4411045f9424d45a0f132d3e40642c38fdfe0febacf78cc95e76
UNFRAMED_ADDRESS=0x051734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b
FLEX_ADDRESS=0x04b1b3fdf34d00288a7956e6342fb366a1510a9387d321c87f3301d990ac19d4
FIBROUS_ADDRESS=0x00f6f4cf62e3c010e0ac2451cc7807b5eec19a40b0faacd00cca3914280fdf5a

EMOJI_NUMBERS = {
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣",
    "7": "7️⃣",
    "8": "8️⃣",
    "9": "9️⃣",
    "0": "0️⃣"
}

HELZY = [
'''
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |  ____  ____  | || |  _________   | || |   _____      | || |   ________   | || |  ____  ____  | |
| | |_   ||   _| | || | |_   ___  |  | || |  |_   _|     | || |  |  __   _|  | || | |_  _||_  _| | |
| |   | |__| |   | || |   | |_  \_|  | || |    | |       | || |  |_/  / /    | || |   \ \  / /   | |
| |   |  __  |   | || |   |  _|  _   | || |    | |   _   | || |     .'.' _   | || |    \ \/ /    | |
| |  _| |  | |_  | || |  _| |___/ |  | || |   _| |__/ |  | || |   _/ /__/ |  | || |    _|  |_    | |
| | |____||____| | || | |_________|  | || |  |________|  | || |  |________|  | || |   |______|   | |
| |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
''',
'''
 █████   █████ ██████████ █████       ███████████ █████ █████
░░███   ░░███ ░░███░░░░░█░░███       ░█░░░░░░███ ░░███ ░░███ 
 ░███    ░███  ░███  █ ░  ░███       ░     ███░   ░░███ ███  
 ░███████████  ░██████    ░███            ███      ░░█████   
 ░███░░░░░███  ░███░░█    ░███           ███        ░░███    
 ░███    ░███  ░███ ░   █ ░███      █  ████     █    ░███    
 █████   █████ ██████████ ███████████ ███████████    █████   
░░░░░   ░░░░░ ░░░░░░░░░░ ░░░░░░░░░░░ ░░░░░░░░░░░    ░░░░░    
''',
]
