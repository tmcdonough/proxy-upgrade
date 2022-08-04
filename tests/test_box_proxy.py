from scripts.helpful_scripts import get_account, encode_function_data
from brownie import Box, ProxyAdmin, TransparentUpgradeableProxy, Contract


def test_proxy_delegates_calls():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,  # the address of the smart contract that houses the logic.
        proxy_admin.address,  # the address of the administrator of the proxy contract i.e. who can upgrade the contract.
        box_encoded_initializer_function,  # if you are initializing the contract with one of the contracts functions, you have to encode that function + any required arguments in bytes and pass to the deploy function here.
        {"from": account, "gas_limit": 1000000},
    )

    proxy_box = Contract.from_abi("Box", proxy.address, box.abi)
    assert proxy_box.retrieve() == 0
    proxy_box.store(1, {"from": account})
    assert proxy_box.retrieve() == 1
