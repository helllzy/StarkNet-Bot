from fake_useragent import UserAgent
from requests import get
from time import sleep
from json import dump

with open('data/addresses.txt') as file:
    addresses = [str(line.strip()) for line in file]

# OR YOU CAN USE THE SECOND WAY:
# from account import CustomAccount
# KEYS = [key["private_key"] for key in WALLETS.values()]
# addresses = [hex(CustomAccount(key).address) for key in KEYS]

contracts = {
    "dmail": 0x0454F0BD015E730E5ADBB4F080B075FDBF55654FF41EE336203AA2E1AC4D4309,
    "starknet_id": 0x05DBDEDC203E92749E2E746E2D40A768D966BD243DF04A6B712E222BC040A9AF,
    "zk_lend": 0x04c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05,
    "jedi_swap": 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023,
    "10k_swap": 0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1,
    "myswap": 0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28,
    "sith_swap": 0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627,
    "avnu_swap": 0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f,
    "starkex_swap": 0x07ebd0e95dfc4411045f9424d45a0f132d3e40642c38fdfe0febacf78cc95e76,
    "flex_market": 0x04b1b3fdf34d00288a7956e6342fb366a1510a9387d321c87f3301d990ac19d4,
    "fibrous_swap": 0x00f6f4cf62e3c010e0ac2451cc7807b5eec19a40b0faacd00cca3914280fdf5a,
    "unframed_market": 0x051734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b,
    "starkverse": 0x060582df2cd4ad2c988b11fdede5c43f56a432e895df255ccd1af129160044b8
}

def fetch_data(address: str) -> list:
    while True:

        used_contracts, unused_contracts = [], []

        ua = UserAgent(os=["windows"], browsers=['chrome'])

        headers = {
                'authority': 'cloud.argent-api.com',
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'argent-client': 'argent-x',
                'argent-network': 'mainnet',
                'argent-version': '5.10.4',
                'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': ua.random,
            }
        
        params = {
                'page': '0',
                'size': '200',
                'direction': 'DESC',
                'withTransfers': 'false',
            }

        try:

            response = get(
                f'https://cloud.argent-api.com/v1/explorer/starknet/accounts/mainnet/{address}/transactions',
                params=params,
                headers=headers,
            )

            data = response.json()

            for transaction in data:

                for event in transaction['events']:
                    contract = event['address']
                    used_contracts.append(int(contract, 16))

                calls = transaction.get('calls')

                if calls:
                    for call in calls:
                        contract = call.get('address')
                        used_contracts.append(int(contract, 16))

            for k, v in contracts.items():
                if v not in used_contracts:
                    unused_contracts.append(k)

            return unused_contracts

        except Exception as e:
            print(f'{address} | error: {str(e)}')
            sleep(5)


def main() -> None:
    accs = {}

    for num, address in enumerate(addresses, start=1):
        accs[str(address)] = data = fetch_data(address)
        print(num, address, ' '.join(data), sep=' | ')
        sleep(1)

    with open('data/unused_contracts.json', 'w') as file:
        dump(accs, file, indent=4)


if __name__ == '__main__':
    main()
