import json
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Algod token, if required
AMOUNT_ALGOS = 5000000  # Amount of Algos in microAlgos (5 Algos)
AMOUNT_ASA = 2  # Amount of ASA units to transfer
ASA_TOTAL = 1000  # Total units of the ASA to create

# Initialize Algod client
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Function to generate a new Algorand account
def generate_account():
    private_key, address = account.generate_account()
    print(f"Address: {address}")
    print(f"Mnemonic: {mnemonic.from_private_key(private_key)}")
    return private_key, address

# Create two new accounts
private_key_a, address_a = generate_account()
private_key_b, address_b = generate_account()
def main():
    print("Generated accounts:")
    print(f"Account A: {address_a}")
    print(f"Account B: {address_b}")