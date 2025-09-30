"""
AP2 Mandate data structures

This module defines the core mandate types for the Agent Payments Protocol:
- IntentMandate: Agent authorization constraints
- CartMandate: Specific purchase approval
- PaymentMandate: Transaction execution record
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PaymentMethod(Enum):
    """Supported payment methods in AP2"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    STABLECOIN = "stablecoin"
    CRYPTO = "crypto"


@dataclass
class IntentMandate:
    """
    Intent Mandate: Captures conditions under which an AI Agent 
    can make purchases on behalf of the user.
    
    This is the foundational authorization that gives an agent
    permission to shop within defined constraints.
    """
    user_id: str
    agent_id: str
    max_amount: float
    currency: str
    valid_until: str
    merchant_whitelist: List[str]
    categories: List[str]
    timestamp: str
    signature: Optional[str] = None
    
    def sign(self, private_key: str) -> str:
        """
        Create cryptographic signature for the mandate.
        
        In production, this would use proper asymmetric cryptography.
        This implementation uses SHA256 for demonstration purposes.
        
        Args:
            private_key: The user's private key
            
        Returns:
            The signature hash
        """
        data = json.dumps(asdict(self), sort_keys=True)
        signature = hashlib.sha256(f"{data}{private_key}".encode()).hexdigest()
        self.signature = signature
        return signature
    
    def verify(self) -> bool:
        """Verify that the mandate has been signed"""
        return self.signature is not None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class CartItem:
    """Individual item in a shopping cart"""
    name: str
    price: float
    quantity: int
    merchant_id: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    def total_price(self) -> float:
        """Calculate total price for this item"""
        return self.price * self.quantity


@dataclass
class CartMandate:
    """
    Cart Mandate: Captures user's final, explicit authorization 
    for a specific cart with exact items and prices.
    
    This provides non-repudiable proof of the user's intent
    for a specific purchase.
    """
    user_id: str
    agent_id: str
    items: List[Dict]
    total_amount: float
    currency: str
    merchant_id: str
    timestamp: str
    intent_mandate_ref: str  # Reference to the Intent Mandate signature
    signature: Optional[str] = None
    
    def sign(self, private_key: str) -> str:
        """
        Create cryptographic signature for the cart.
        
        Args:
            private_key: The user's private key
            
        Returns:
            The signature hash
        """
        data = json.dumps(asdict(self), sort_keys=True)
        signature = hashlib.sha256(f"{data}{private_key}".encode()).hexdigest()
        self.signature = signature
        return signature
    
    def verify_against_intent(self, intent: IntentMandate) -> bool:
        """
        Verify that this cart complies with the intent mandate constraints.
        
        Checks:
        - Total amount doesn't exceed max amount
        - Merchant is in whitelist
        - Currency matches
        
        Args:
            intent: The Intent Mandate to verify against
            
        Returns:
            True if cart is valid, False otherwise
        """
        if self.total_amount > intent.max_amount:
            return False
        if self.merchant_id not in intent.merchant_whitelist:
            return False
        if self.currency != intent.currency:
            return False
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class PaymentMandate:
    """
    Payment Mandate: Shared with payment network and issuer 
    to signal AI agent involvement and transaction context.
    
    This creates a complete audit trail for the transaction.
    """
    transaction_id: str
    cart_mandate_ref: str  # Reference to the Cart Mandate signature
    payment_method: PaymentMethod
    amount: float
    currency: str
    agent_present: bool
    human_present: bool
    timestamp: str
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['payment_method'] = self.payment_method.value
        return data
    
    def is_autonomous(self) -> bool:
        """Check if this was an autonomous agent transaction"""
        return self.agent_present and not self.human_present
