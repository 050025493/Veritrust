import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

# 1. Connect to Blockchain
w3 = Web3(Web3.HTTPProvider(os.getenv('ALCHEMY_URL')))
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
contract_address = os.getenv('CONTRACT_ADDRESS')

# 2. PULL DIRECTLY FROM .ENV
abi_string = os.getenv('CONTRACT_ABI')
CONTRACT_ABI = json.loads(abi_string)

# 3. Initialize Contract
contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)

def run_test():
    print(f"🔗 Connected to Sepolia: {w3.is_connected()}")
    
    # Fake data for our test
    test_video_hash = "test_hash_001_abc123"
    is_fake = True
    confidence = 98
    
    print("⏳ Building the transaction...")
    
    try:
        nonce = w3.eth.get_transaction_count(wallet_address)
        
        tx = contract.functions.logEvidence(
            test_video_hash, 
            is_fake, 
            confidence
        ).build_transaction({
            'chainId': 11155111, 
            'gas': 500000,       
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
        
        print("✍️ Signing the transaction with Private Key...")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        
        print("🚀 Sending to the blockchain...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt_hash = w3.to_hex(tx_hash)
        
        print("\n✅ SUCCESS! Evidence logged to the blockchain.")
        print(f"🔍 View your real live transaction here:")
        print(f"https://sepolia.etherscan.io/tx/{receipt_hash}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_test()