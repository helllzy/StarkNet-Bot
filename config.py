######################################################
# Main settings connected to account & transactions ##
######################################################

# True if you changed your accs private keys.
# provide your addresses in data/adresses.txt
CHANGED_KEY = False

# all transactions will be completed via this RPC
RPC = "https://starknet-mainnet.public.blastapi.io"

# delay between accounts
DELAY = [100, 200]

# delay between modules
MOD_DELAY = [25, 80]

# all transactions will be completed below this gas price
MAX_GWEI = 7.55

# True if you want to achieve an exact nonce
# if you chose this, modules will be calculated:
# EXACT_NONCE_COUNT-your nonce and bot will choose modules from MODULES * 1000
EXACT_NONCE = False

# transactions count after script running
EXACT_NONCE_COUNT = [70, 90]

# True if you want to randomize moudules execution
RANDOMIZE_MODULES = True

# True if you want to randomize wallets execution
RANDOMIZE_WALLETS = True

# True if you want to use proxy. everyone account must have a proxy.
# provide your proxies in data/proxies.txt
USE_PROXY = False

# True if you want to deploy wallets
DEPLOY_WALLETS = False

'''
-----------------|available modules|-----------------|
-- Don`t use "starkverse" cause project`s website    |
-- doesn`t work, it looks like sybil activity        |
-----------------------|swaps|-----------------------|
"jedi_swap",                                         |
"10k_swap",                                          |
"myswap",                                            |
"sith_swap",                                         |
"avnu_swap",                                         |
"starkex_swap",                                      |
"fibrous_swap"                                       |
----------------------|lending|----------------------|
"zk_lending"                                         |
---------------------|liquidity|---------------------|
"jedi_liquidity",                                    |
"10k_liquidity",                                     |
"sith_liquidity"                                     |
----------------|cheap transactions|-----------------|
"starkverse",                                        |
"collateral",                                        |
"dmail",                                             |
"starknet_id",                                       |
"flex_market",                                       |
"unframed_market",                                   |  
"increase_limit"                                     |
-----------------------------------------------------|
'''

# write there all modules from the table above you would like to complete
MODULES = [
    "collateral",
    "dmail",
    "starknet_id",
    "flex_market",
    "unframed_market",
    "increase_limit"
]

# True if you want to skip some modules. it's good for account's randomization
# if you chose this, modules will be calculated from MODULES with MODS_COUNT
SKIP_MODS = True

# how many modules do you need for each account?
# each account will choose his own count
MODS_COUNT = [3, 5]

######################################################
######## Settings below for swap or lending ##########
######################################################

# % of your balance for lending
LENDING_PERCENTAGES = [50, 70]

# True if you want to repeat zk_lending
ZK_VOLUME = False

# how many zk_lending repeats do you need
ZK_REPEATS = [2, 3]

# these tokens will be used for swap or liquidity
ALLOWED_TOKENS = ['USDT', 'USDC', 'DAI', 'WBTC']

# % of your balance for swap
# swaps will be made first from ALLOWED_TOKENS in your wallet if you have any,
# in another case bot will use your balance * SWAP_PERCENTAGES
SWAP_PERCENTAGES = [1, 5]

######################################################
# Settings below connected to OKX withdraw & deposit #
######################################################

# True if you want to use your OKX to withdraw ETH to your accs.
# provide your addresses in data/addresses.txt
WITHDRAW_FROM_OKX = False

# True if you want to transfer your ETH from subs to main OKX acc
SUB_ACCS = False

# how many ETH do you want to withdraw from OKX
# each account will choose his own amount
WITHDRAW_AMOUNT = [1.6, 2]

# True if you want to transfer ETH from your accs to OKX.
# provide your okx_addresses in data/okx_addresses.txt
TRANSFER_TO_OKX = False

# how many ETH do you want to keep in your wallet
# after transfer to OKX
AMOUNT_TO_KEEP = [0.011, 0.015]

# OKX fee of ETH withdraw to StarkNet
FEE = 0.0001

# https://www.okx.com/account/my-api 
# there you can take your API keys. It needs only for OKX withdraw
OKX_KEYS = {
    'api_key'   : '',
    'api_secret': '',
    'password'  : ''
}

######################################################
########### Settings below for TG messages ###########
######################################################

# https://t.me/BotFather
# there you can take API key for your TG bot
BOT_TOKEN = ''

# https://t.me/getmy_idbot
# there you can take your TG ID
CHAT_ID = 0

# ETH price needs to send you calculated FEE for each account
CURRENT_ETH_PRICE = 1570
