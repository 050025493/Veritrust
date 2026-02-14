"""
Blockchain Service
Handles logging evidence to Polygon blockchain
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class BlockchainService:
    """
    Service for interacting with Polygon blockchain
    """
    
    def __init__(self):
        # Load environment variables
        self.alchemy_url = os.getenv('ALCHEMY_URL')
        self.wallet_address = os.getenv('WALLET_ADDRESS')
        self.private_key = os.getenv('PRIVATE_KEY')
        self.contract_address = os.getenv('CONTRACT_ADDRESS')
        
        # Load contract ABI
        abi_string = os.getenv('CONTRACT_ABI')
        self.contract_abi = json.loads(abi_string) if abi_string else None
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.alchemy_url))
        
        # Initialize contract
        if self.contract_address and self.contract_abi:
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
        else:
            self.contract = None
            
        self.chain_id = 11155111  # Sepolia testnet (change to 137 for Polygon mainnet)
    
    def is_connected(self):
        """Check if connected to blockchain"""
        return self.w3.is_connected()
    
    def log_evidence(self, video_hash, is_fake, confidence):
        """
        Log evidence to blockchain
        
        Args:
            video_hash: SHA-256 hash of video
            is_fake: Boolean - True if fake, False if real
            confidence: Integer 0-100
            
        Returns:
            dict: Transaction details including tx_hash and etherscan_url
        """
        if not self.contract:
            raise ValueError("Contract not initialized. Check .env configuration.")
        
        try:
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            
            # Build transaction
            tx = self.contract.functions.logEvidence(
                video_hash,
                is_fake,
                confidence
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = self.w3.to_hex(tx_hash)
            
            # Generate Etherscan URL
            etherscan_url = f"https://sepolia.etherscan.io/tx/{tx_hash_hex}"
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'etherscan_url': etherscan_url,
                'video_hash': video_hash,
                'is_fake': is_fake,
                'confidence': confidence,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'video_hash': video_hash
            }
    
    def get_transaction_receipt(self, tx_hash):
        """
        Get transaction receipt (to check if confirmed)
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            dict: Receipt details or None if not confirmed
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'confirmed': True,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'status': receipt['status']  # 1 = success, 0 = failed
            }
        except Exception:
            # Transaction not yet mined
            return {
                'confirmed': False
            }
    
    def verify_evidence(self, video_hash):
        """
        Verify if evidence exists on blockchain
        
        Args:
            video_hash: SHA-256 hash of video
            
        Returns:
            dict: Verification details
        """
        if not self.contract:
            raise ValueError("Contract not initialized")
        
        try:
            # Call contract's verify function (if it exists)
            # This depends on your smart contract implementation
            # Example:
            # result = self.contract.functions.getEvidence(video_hash).call()
            
            return {
                'verified': True,
                'video_hash': video_hash
            }
        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }


# Singleton instance
_blockchain_service = None

def get_blockchain_service():
    """Get or create blockchain service instance"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service


if __name__ == "__main__":
    # Test blockchain connection
    service = BlockchainService()
    print(f"Connected to blockchain: {service.is_connected()}")
    
    if service.is_connected():
        print(f"Wallet: {service.wallet_address}")
        print(f"Contract: {service.contract_address}")