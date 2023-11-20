import json
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn

# Constants and Algod client initialization
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Algod token, if required
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Recover accounts from mnemonic
mnemonic_a = "satoshi veteran decide gorilla one crawl you layer change pupil burger message cry unlock miracle lobster rain clock tool social year trend flip abstract mail"
mnemonic_b = "evoke devote blanket decline help trust fox grab absent hamster initial toast fuel nation analyst divide forest shrug brisk myth drop logic visa above robust"
mnemonic_c = "velvet photo genuine bronze path fiscal two voice helmet never valley fold unfold spatial vocal reject fuel goat reason churn city dirt rotate able awake"
mnemonic_d = "hurry myth visual express own final build mention stairs hockey review unit erosion loud correct note alpha then clip spin media innocent absorb abandon mention"

private_key_a = mnemonic.to_private_key(mnemonic_a)
address_a = account.address_from_private_key(private_key_a)
private_key_b = mnemonic.to_private_key(mnemonic_b)
address_b = account.address_from_private_key(private_key_b)
private_key_c = mnemonic.to_private_key(mnemonic_c)
address_c = account.address_from_private_key(private_key_c)
private_key_d = mnemonic.to_private_key(mnemonic_d)
address_d = account.address_from_private_key(private_key_d)

# Function to issue an ASA
def create_asa(creator_private_key, creator_address):
    sp = client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=sp,
        total=1000,  # Total supply for the fractional NFT
        default_frozen=False,
        unit_name="FNFT",
        asset_name="FractionalNFT",
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        decimals=0  # Non-divisible
    )
    stxn = txn.sign(creator_private_key)
    txid = client.send_transaction(stxn)
    wait_for_confirmation(client, txid)
    ptx = client.pending_transaction_info(txid)
    return ptx["asset-index"]

# Function to opt-in for an ASA
def opt_in_asa(asset_id, account_private_key, account_address):
    sp = client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=account_address,
        sp=sp,
        receiver=account_address,
        amt=0,
        index=asset_id
    )
    stxn = txn.sign(account_private_key)
    txid = client.send_transaction(stxn)
    wait_for_confirmation(client, txid)

# Function to transfer ASA
def transfer_asa(asset_id, sender_private_key, sender_address, receiver_address, amount):
    sp = client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=sp,
        receiver=receiver_address,
        amt=amount,
        index=asset_id
    )
    stxn = txn.sign(sender_private_key)
    txid = client.send_transaction(stxn)
    wait_for_confirmation(client, txid)

# Function to wait for a transaction to be confirmed
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(f"Transaction confirmed in round {txinfo.get('confirmed-round')}.")
def check_holdings(asset_id, addresses):
    for address in addresses:
        account_info = client.account_info(address)
        holding = next((asset for asset in account_info.get('assets', []) if asset['asset-id'] == asset_id), None)
        if holding:
            print(f"Address {address} holds {holding['amount']} units of the Fractional NFT.")
        else:
            print(f"Address {address} does not hold any units of the Fractional NFT.")
# Main function
def main():
    # Create ASA 'UCTZAR'
    print("Creating Fractional NFT (ASA) 'UCTZAR'...")
    uctzar_id = create_asa(private_key_a, address_a)
    print(f"Fractional NFT (ASA) ID: {uctzar_id}")

    # Opt-in for ASA for accounts B, C, and D
    print("Opting in for UCTZAR for accounts B, C, and D...")
    opt_in_asa(uctzar_id, private_key_b, address_b)
    opt_in_asa(uctzar_id, private_key_c, address_c)
    opt_in_asa(uctzar_id, private_key_d, address_d)

    # Distribute Fractional NFTs to accounts B, C, and D
    print("Distributing Fractional NFTs to accounts B, C, and D...")
    transfer_asa(uctzar_id, private_key_a, address_a, address_b, 300)  # Distributing 300 units to B
    transfer_asa(uctzar_id, private_key_a, address_a, address_c, 200)  # Distributing 200 units to C
    transfer_asa(uctzar_id, private_key_a, address_a, address_d, 100)  # Distributing 100 units to D

    # Check each account's holding of the fractional NFT
    print("Verifying holdings of each account...")
    check_holdings(uctzar_id, [address_b, address_c, address_d])


if __name__ == "__main__":
    main()
