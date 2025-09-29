import razorpay
import hmac
import hashlib
from typing import Dict, Any
from .config import settings
from .models import Package, PackageTier


class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    
    def create_order(self, amount: int, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
        """Create a Razorpay order"""
        order_data = {
            "amount": amount,  # Amount in paise
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1  # Auto capture payment
        }
        
        order = self.client.order.create(data=order_data)
        return order
    
    def verify_payment_signature(
        self, 
        razorpay_order_id: str, 
        razorpay_payment_id: str, 
        razorpay_signature: str
    ) -> bool:
        """Verify Razorpay payment signature"""
        try:
            # Create the signature string
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                settings.razorpay_key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, razorpay_signature)
        except Exception:
            return False
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details from Razorpay"""
        return self.client.payment.fetch(payment_id)


class CommissionCalculator:
    """Calculate commissions based on package tiers and referral levels"""
    
    @staticmethod
    def calculate_commissions(package: Package, referrer_id: int, indirect_referrer_id: int = None) -> list:
        """
        Calculate commissions for direct and indirect referrers
        
        Args:
            package: The purchased package
            referrer_id: Direct referrer user ID
            indirect_referrer_id: Indirect referrer user ID (referrer's referrer)
        
        Returns:
            List of commission dictionaries
        """
        commissions = []
        
        # Direct commission (Level 1)
        if referrer_id:
            commissions.append({
                "earner_id": referrer_id,
                "level": 1,
                "amount": package.direct_commission
            })
        
        # Indirect commission (Level 2)
        if indirect_referrer_id:
            commissions.append({
                "earner_id": indirect_referrer_id,
                "level": 2,
                "amount": package.indirect_commission
            })
        
        return commissions


# Initialize service
razorpay_service = RazorpayService()
commission_calculator = CommissionCalculator()