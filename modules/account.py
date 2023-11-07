from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId

from aiohttp import ClientSession, TCPConnector

from modules.utils import logger, info
from config import RPC, CHANGED_KEY
from data.data import (
    USE_PROXY,
    WALLETS,
    ARGENT_PROXY_CLASS_HASH,
    ARGENT_IMPLEMENTATION_CLASS_HASH,
    SELECTOR
)


class CustomSession(ClientSession):
    def __init__(self, *args, proxy=None, **kwargs):
        super().__init__(*args, **kwargs)
        _proxy = f'{proxy[proxy.find(":")+6:]}@{proxy[:proxy.find(":")+5]}'
        proxy = "http://" + _proxy
        self.proxy = proxy


    async def _request(self, *args, **kwargs):
        return await super()._request(*args, **kwargs, proxy=self.proxy)


class CustomAccount(Account):
    def __init__(self, private_key: int):
        self.argent_proxy_class_hash = ARGENT_PROXY_CLASS_HASH
        self.key_pair = KeyPair.from_private_key(private_key)
        call_data = [self.key_pair.public_key, 0]
        self.constructor_calldata = [
            ARGENT_IMPLEMENTATION_CLASS_HASH, SELECTOR, len(call_data), *call_data]

        for wallet in WALLETS.values():
            if wallet["private_key"] == private_key:
                self._wallet = wallet
                break

        if not USE_PROXY:
            client = FullNodeClient(node_url=RPC)
        else:
            connector = TCPConnector(limit=10)
            self.custom_session = CustomSession(proxy=self._wallet["proxy"], connector=connector)
            client = FullNodeClient(node_url=RPC, session=self.custom_session)

        if CHANGED_KEY:
            address = self._wallet["address"]
        else:
            address = self.__get_argent_address()

        super().__init__(
            address=address,
            client=client,
            key_pair=self.key_pair,
            chain=StarknetChainId.MAINNET
        )


    def __get_argent_address(self) -> int:
        address = compute_address(
            class_hash=self.argent_proxy_class_hash,
            constructor_calldata=self.constructor_calldata,
            salt=self.key_pair.public_key
        )

        return address


    async def deploy(self) -> int:
        gateway_client = GatewayClient(net="mainnet")
        nonce = await gateway_client.get_contract_nonce(self.address)

        if nonce > 0:
            info(f"| {hex(self.address)} already deployed", "cyan")
            return 1

        deploy_account_tx = await self.sign_deploy_account_transaction(
            class_hash=self.argent_proxy_class_hash,
            contract_address_salt=self.key_pair.public_key,
            constructor_calldata=self.constructor_calldata,
            auto_estimate=True
        )

        execution = await gateway_client.deploy_account(deploy_account_tx)

        info(
        f"| Deploy | Waiting transaction: "
        f"https://starkscan.co/tx/{hex(execution.transaction_hash)}", "magenta"
        )

        await gateway_client.wait_for_tx(execution.transaction_hash)

        logger.success(f"| Deploy | Transaction accepted")
        return 1
