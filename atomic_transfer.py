import json
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn


# Constants
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Algod token, if required
AMOUNT_ALGOS = 5000000  # Amount of Algos in microAlgos (5 Algos)
AMOUNT_ASA = 2  # Amount of ASA units to transfer
ASA_TOTAL = 1000  # Total units of the ASA to create

# Initialize Algod client
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Function to generate a new Algorand account

mnemonic_a = "satoshi veteran decide gorilla one crawl you layer change pupil burger message cry unlock miracle lobster rain clock tool social year trend flip abstract mail"
mnemonic_b = "evoke devote blanket decline help trust fox grab absent hamster initial toast fuel nation analyst divide forest shrug brisk myth drop logic visa above robust"

# Recover accounts from mnemonic


private_key_a = mnemonic.to_private_key(mnemonic_a)
address_a = account.address_from_private_key(private_key_a)
private_key_b = mnemonic.to_private_key(mnemonic_b)
address_b = account.address_from_private_key(private_key_b)
# Function to issue an ASA
def create_asa(creator_private_key, creator_address):
    sp = client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=sp,
        total=ASA_TOTAL,
        default_frozen=False,
        unit_name="UCTZAR",
        asset_name="UCTokenZAR",
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        decimals=0
    )
    stxn = txn.sign(creator_private_key)
    txid = client.send_transaction(stxn)
    wait_for_confirmation(client, txid)
    ptx = client.pending_transaction_info(txid)
    asset_id = ptx["asset-index"]
    return asset_id

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

# Function to perform atomic transfer
def atomic_transfer(asset_id, private_key_a, address_a, private_key_b, address_b):
    sp = client.suggested_params()
    txn1 = transaction.PaymentTxn(address_a, sp, address_b, AMOUNT_ALGOS)
    txn2 = transaction.AssetTransferTxn(address_b, sp, address_a, AMOUNT_ASA, asset_id)
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid
    stxn1 = txn1.sign(private_key_a)
    stxn2 = txn2.sign(private_key_b)
    signed_group = [stxn1, stxn2]
    tx_id = client.send_transactions(signed_group)
    wait_for_confirmation(client, tx_id)

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

# Main function
def main():
    # Print account details
    print("Using predefined accounts:")
    print(f"Account A: {address_a}")
    print(f"Account B: {address_b}")

    # Create ASA 'UCTZAR'
    print("Creating ASA 'UCTZAR'...")
    uctzar_id = create_asa(private_key_a, address_a)
    print(f"UCTZAR ID: {uctzar_id}")

    # Opt-in for ASA
    print("Opting in Account B for UCTZAR...")
    opt_in_asa(uctzar_id, private_key_b, address_b)

    # Transfer UCTZAR to Account B
    print("Transferring 10 UCTZAR to Account B...")
    transfer_asa(uctzar_id, private_key_a, address_a, address_b, 10)

    # Prepare for atomic transfer
    print("Ready for atomic transfer. Ensure Account A is funded with Algos before proceeding.")
    input("Press Enter after ensuring the prerequisites are met...")

    # Perform atomic transfer
    print("Performing atomic transfer...")
    atomic_transfer(uctzar_id, private_key_a, address_a, private_key_b, address_b)

    print("Atomic transfer completed.")


if __name__ == "__main__":
    main()
          
