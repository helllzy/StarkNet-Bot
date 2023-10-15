from datetime import datetime as dt
from base64 import b64encode
from random import uniform
from asyncio import sleep
from hmac import new
from requests import post, get
from loguru import logger

from config import WITHDRAW_AMOUNT, OKX_KEYS, FEE, SUB_ACCS
from data.data import Module


class OKX(Module):
    def __init__(self, account):
        self.account = account
        self.acc_addr = self.account._wallet["address"]
        self.api_key = OKX_KEYS['api_key']
        self.secret_key = OKX_KEYS['api_secret']
        self.passphrase = OKX_KEYS['password']


    async def signature(
            self, timestamp: str, method: str, request_path: str, body: str = ""
            ) -> str:

        message = timestamp + method.upper() + request_path + body
        mac = new(
            bytes(self.secret_key, encoding="utf-8"),
            bytes(message, encoding="utf-8"),
            digestmod="sha256",
        )
        d = mac.digest()

        return b64encode(d).decode("utf-8")


    async def okx_data(
            self, request_path, body='', meth="GET"
            ) -> int | None:

        try:
            dt_now = dt.utcnow()
            ms = str(dt_now.microsecond).zfill(6)[:3]
            timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

            headers = {
                "Content-Type": "application/json",
                "OK-ACCESS-KEY": self.api_key,
                "OK-ACCESS-SIGN": await self.signature(
                    timestamp, meth, request_path, body),
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.passphrase,
                'x-simulated-trading': '0'
            }

        except Exception as ex:
            logger.error(ex)

        return headers


    async def start(self, module, symbol='ETH'):
        amount = round(uniform(*WITHDRAW_AMOUNT), 7)

        if SUB_ACCS:

            try:

                headers = await self.okx_data(
                    request_path="/api/v5/users/subaccount/list", meth="GET")
                list_sub =  get(
                    "https://www.okx.cab/api/v5/users/subaccount/list", timeout=10, headers=headers)
                list_sub = list_sub.json()


                for sub_data in list_sub['data']:

                    name_sub = sub_data['subAcct']

                    headers = await self.okx_data(
                        request_path=f"/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy={symbol}", meth="GET")
                    sub_balance = get(
                        f"https://www.okx.cab/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy={symbol}",timeout=10, headers=headers)
                    sub_balance = sub_balance.json()
                    sub_balance = sub_balance['data'][0]['bal']

                    print(f' {name_sub} balance : {sub_balance} {symbol} |', end='')

                    body = {"ccy": f"{symbol}", "amt": str(sub_balance), "from": 6, "to": 6, "type": "2", "subAcct": name_sub}
                    headers = await self.okx_data(
                        request_path="/api/v5/asset/transfer", body=str(body), meth="POST")
                    a = post(
                        "https://www.okx.cab/api/v5/asset/transfer",data=str(body), timeout=10, headers=headers)
                    a = a.json()
                    await sleep(2)
                print()

            except Exception as error:
                logger.error(f'{error}. list_sub : {list_sub}')

        try:
            headers = await self.okx_data(request_path=f"/api/v5/account/balance?ccy={symbol}")
            balance = get(
                f'https://www.okx.cab/api/v5/account/balance?ccy={symbol}', timeout=10, headers=headers)

            balance = balance.json()["data"][0]["totalEq"]

            if balance != 0:
                body = {"ccy": f"{symbol}", "amt": float(balance), "from": 18, "to": 6, "type": "0", "subAcct": "", "clientId": "", "loanTrans": "", "omitPosRisk": ""}
                headers = await self.okx_data(
                    request_path="/api/v5/asset/transfer", body=str(body), meth="POST")
                a = post(
                    "https://www.okx.cab/api/v5/asset/transfer",data=str(body), timeout=10, headers=headers)

            body = {"ccy":symbol, "amt":amount, "fee":FEE, "dest":"4", "chain":f"{symbol}-{'Starknet'}", "toAddr":self.acc_addr}
            headers = await self.okx_data(
                request_path="/api/v5/asset/withdrawal", meth="POST", body=str(body))
            a = post(
                "https://www.okx.cab/api/v5/asset/withdrawal",data=str(body), timeout=10, headers=headers)
            result = a.json()

            if result['code'] == '0':
                logger.success(f'{self.acc_addr} | {module} | withdraw success | {amount} {symbol}')

                while True:
                    await sleep(30)

                    try:
                        if (await self.account.get_balance()) / 1e18 > amount:
                            logger.success(f'{self.acc_addr} | received {amount} {symbol}')
                            return 1

                        logger.info(f'{self.acc_addr} | is waiting for deposit')

                    except Exception as error:
                        logger.error(
                            f'| an error while balance checking, sleep for 300 seconds and start modules | {error}')
                        await sleep(300)
                        return 1

            else:
                error = result['msg']
                logger.error(f'{self.acc_addr} | withdraw unsuccess | error : {error}')

        except Exception as error:
            logger.error(f'{self.acc_addr} | withdraw unsuccess | error : {error}')
