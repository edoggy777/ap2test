"""
AP2 Test Harness

Provides the core testing functionality for AP2 payment flows,
including mandate creation, validation, and audit trail generation.
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from .mandates import (
    IntentMandate,
    CartMandate,
    PaymentMandate,
    CartItem,
    PaymentMethod,
)


class AP2TestHarness:
    """
    Test harness for AP2 payment flows.
    
    Manages the complete lifecycle of AP2 transactions including:
    - Intent mandate creation and storage
    - Cart mandate creation and validation
    - Payment execution
    - Audit trail generation
    """
    
    def __init__(self, user_id: str = "test_user", agent_id: str = "test_agent"):
        """
        Initialize the test harness.
        
        Args:
            user_id: Identifier for the test user
            agent_id: Identifier for the test agent
        """
        self.user_id = user_id
        self.agent_id = agent_id
        self.private_key = "test_key_12345"  # Simulated private key
        self.data_file = Path.home() / ".ap2test_data.json"
        
        self._load_data()
    
    def _load_data(self):
        """Load existing test data from disk"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load intent mandates
                    self.intent_mandates = [
                        IntentMandate(**m) for m in data.get('intent_mandates', [])
                    ]
                    
                    # Load cart mandates
                    self.cart_mandates = [
                        CartMandate(**m) for m in data.get('cart_mandates', [])
                    ]
                    
                    # Load payment mandates
                    payment_data = data.get('payment_mandates', [])
                    self.payment_mandates = []
                    for p in payment_data:
                        p['payment_method'] = PaymentMethod(p['payment_method'])
                        self.payment_mandates.append(PaymentMandate(**p))
            except Exception as e:
                print(f"Warning: Could not load data file: {e}")
                self._init_empty_data()
        else:
            self._init_empty_data()
    
    def _init_empty_data(self):
        """Initialize empty data structures"""
        self.intent_mandates = []
        self.cart_mandates = []
        self.payment_mandates = []
    
    def _save_data(self):
        """Persist test data to disk"""
        data = {
            'intent_mandates': [m.to_dict() for m in self.intent_mandates],
            'cart_mandates': [m.to_dict() for m in self.cart_mandates],
            'payment_mandates': [m.to_dict() for m in self.payment_mandates]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def reset(self):
        """Clear all test data"""
        self.intent_mandates = []
        self.cart_mandates = []
        self.payment_mandates = []
        if self.data_file.exists():
            self.data_file.unlink()
    
    def create_intent_mandate(
        self,
        max_amount: float,
        currency: str = "USD",
        valid_hours: int = 24,
        merchant_whitelist: List[str] = None,
        categories: List[str] = None
    ) -> IntentMandate:
        """
        Create an Intent Mandate giving the agent shopping authority.
        
        Args:
            max_amount: Maximum amount the agent can spend
            currency: Currency code (e.g., USD, EUR)
            valid_hours: How many hours the mandate is valid
            merchant_whitelist: List of allowed merchant IDs
            categories: List of allowed product categories
            
        Returns:
            The created and signed IntentMandate
        """
        valid_until = (datetime.now() + timedelta(hours=valid_hours)).isoformat()
        
        mandate = IntentMandate(
            user_id=self.user_id,
            agent_id=self.agent_id,
            max_amount=max_amount,
            currency=currency,
            valid_until=valid_until,
            merchant_whitelist=merchant_whitelist or ["default_merchant"],
            categories=categories or ["general"],
            timestamp=datetime.now().isoformat()
        )
        
        mandate.sign(self.private_key)
        self.intent_mandates.append(mandate)
        self._save_data()
        
        return mandate
    
    def get_latest_intent_mandate(self) -> Optional[IntentMandate]:
        """Get the most recently created intent mandate"""
        return self.intent_mandates[-1] if self.intent_mandates else None
    
    def create_cart_mandate(
        self,
        items: List[CartItem],
        merchant_id: str,
        intent_mandate: Optional[IntentMandate] = None
    ) -> Optional[CartMandate]:
        """
        Create a Cart Mandate for specific items.
        
        Validates the cart against the intent mandate constraints.
        
        Args:
            items: List of CartItem objects to purchase
            merchant_id: The merchant ID
            intent_mandate: Optional specific intent to use (defaults to latest)
            
        Returns:
            The created CartMandate if valid, None if validation fails
        """
        if intent_mandate is None:
            if not self.intent_mandates:
                raise ValueError(
                    "No intent mandate found. Create one first with create_intent_mandate()"
                )
            intent_mandate = self.intent_mandates[-1]
        
        # Calculate total
        total_amount = sum(item.price * item.quantity for item in items)
        
        # Create cart mandate
        mandate = CartMandate(
            user_id=self.user_id,
            agent_id=self.agent_id,
            items=[item.to_dict() for item in items],
            total_amount=total_amount,
            currency=intent_mandate.currency,
            merchant_id=merchant_id,
            timestamp=datetime.now().isoformat(),
            intent_mandate_ref=intent_mandate.signature
        )
        
        mandate.sign(self.private_key)
        
        # Validate against intent mandate
        if not mandate.verify_against_intent(intent_mandate):
            return None
        
        self.cart_mandates.append(mandate)
        self._save_data()
        
        return mandate
    
    def get_latest_cart_mandate(self) -> Optional[CartMandate]:
        """Get the most recently created cart mandate"""
        return self.cart_mandates[-1] if self.cart_mandates else None
    
    def execute_payment(
        self,
        cart_mandate: Optional[CartMandate] = None,
        payment_method: PaymentMethod = PaymentMethod.CARD,
        human_present: bool = True
    ) -> PaymentMandate:
        """
        Execute a payment transaction.
        
        Args:
            cart_mandate: Optional specific cart to pay for (defaults to latest)
            payment_method: Payment method to use
            human_present: Whether a human is present for this transaction
            
        Returns:
            The created PaymentMandate
            
        Raises:
            ValueError: If no cart mandate exists
        """
        if cart_mandate is None:
            if not self.cart_mandates:
                raise ValueError(
                    "No cart mandate found. Create one first with create_cart_mandate()"
                )
            cart_mandate = self.cart_mandates[-1]
        
        # Generate transaction ID
        transaction_id = hashlib.sha256(
            f"{time.time()}{cart_mandate.signature}".encode()
        ).hexdigest()[:16]
        
        # Create payment mandate
        payment = PaymentMandate(
            transaction_id=transaction_id,
            cart_mandate_ref=cart_mandate.signature,
            payment_method=payment_method,
            amount=cart_mandate.total_amount,
            currency=cart_mandate.currency,
            agent_present=True,
            human_present=human_present,
            timestamp=datetime.now().isoformat()
        )
        
        self.payment_mandates.append(payment)
        self._save_data()
        
        return payment
    
    def audit_trail(self) -> dict:
        """
        Generate complete audit trail for all transactions.
        
        Returns:
            Dictionary containing summary and detailed transaction history
        """
        return {
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "summary": {
                "intent_mandates": len(self.intent_mandates),
                "cart_mandates": len(self.cart_mandates),
                "payments": len(self.payment_mandates),
                "total_spent": sum(p.amount for p in self.payment_mandates),
                "autonomous_transactions": sum(
                    1 for p in self.payment_mandates if p.is_autonomous()
                )
            },
            "transactions": [
                {
                    "transaction_id": p.transaction_id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "timestamp": p.timestamp,
                    "payment_method": p.payment_method.value,
                    "autonomous": p.is_autonomous()
                }
                for p in self.payment_mandates
            ]
        }
    
    def get_statistics(self) -> dict:
        """Get statistics about test data"""
        return {
            "intent_mandates": len(self.intent_mandates),
            "cart_mandates": len(self.cart_mandates),
            "payments": len(self.payment_mandates),
            "total_spent": sum(p.amount for p in self.payment_mandates),
        }
