from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)
    # print(box.increment())  # this should ref out for initial BoxV1

    # ---- might want to make the proxy admin be a multi sig -----
    # ---- could also set ourselves to be the proxy admin -----

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)
    box_encoded_initializer_function = (
        encode_function_data()
    )  # don't use an initializer. If we were adding, would be e.g. initializer = (box.store, 1)

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,  # could use our address
        box_encoded_initializer_function,
        {
            "from": account,
            "gas_limit": 1000000,
        },  # proxies sometimes have a hard time figuring out the gas limit
        publish_source=True,
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    # proxy_box.increment({"from": account})  # this should fail since V1 box doesnt have this function and we haevnt yet upgraded.

    # upgrade:
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been updated")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(
        proxy_box.retrieve()
    )  # this should be 2. In original proxy box we started with 1. That gets stored in the original proxy. When we increment on the new proxy it still impacts the original
