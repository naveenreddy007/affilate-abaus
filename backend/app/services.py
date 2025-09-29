from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import User, Package, Order, Commission, PackageTier, OrderStatus
from .auth import get_password_hash
from .razorpay_service import razorpay_service, commission_calculator


class UserService:
    """Service for user management operations"""
    
    @staticmethod
    def create_user(
        session: Session,
        email: str,
        full_name: str,
        password: str,
        referrer_id: Optional[int] = None
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == email)).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            referrer_id=referrer_id,
            is_active=True
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return session.exec(select(User).where(User.email == email)).first()
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return session.exec(select(User).where(User.id == user_id)).first()
    
    @staticmethod
    def update_user_package(
        session: Session,
        user_id: int,
        package_tier: PackageTier
    ) -> User:
        """Update user's package tier"""
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise ValueError("User not found")
        
        user.package_tier = package_tier
        user.purchased_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


class PackageService:
    """Service for package management operations"""
    
    @staticmethod
    def get_all_packages(session: Session) -> List[Package]:
        """Get all packages"""
        return session.exec(select(Package)).all()
    
    @staticmethod
    def get_package_by_tier(session: Session, tier: PackageTier) -> Optional[Package]:
        """Get package by tier"""
        return session.exec(select(Package).where(Package.tier == tier)).first()
    
    @staticmethod
    def create_default_packages(session: Session):
        """Create default packages if they don't exist"""
        packages_data = [
            {
                "tier": PackageTier.SILVER,
                "name": "Silver Package",
                "description": "Basic learning package with essential courses",
                "base_price": 254237,  # ₹2,542.37 (before GST)
                "direct_commission": 50000,  # ₹500
                "indirect_commission": 25000,  # ₹250
                "features": '["Access to basic courses", "Community support", "Mobile app access", "Certificate of completion"]'
            },
            {
                "tier": PackageTier.GOLD,
                "name": "Gold Package",
                "description": "Premium learning package with advanced courses",
                "base_price": 423559,  # ₹4,235.59 (before GST)
                "direct_commission": 100000,  # ₹1,000
                "indirect_commission": 50000,  # ₹500
                "features": '["All Silver features", "Advanced courses", "1-on-1 mentoring", "Priority support", "Exclusive webinars"]'
            },
            {
                "tier": PackageTier.PLATINUM,
                "name": "Platinum Package",
                "description": "Ultimate learning package with all premium features",
                "base_price": 677966,  # ₹6,779.66 (before GST)
                "direct_commission": 150000,  # ₹1,500
                "indirect_commission": 75000,  # ₹750
                "features": '["All Gold features", "Master classes", "Personal career coaching", "Lifetime access", "VIP community access"]'
            }
        ]
        
        for package_data in packages_data:
            existing_package = session.exec(
                select(Package).where(Package.tier == package_data["tier"])
            ).first()
            
            if not existing_package:
                package = Package(**package_data)
                session.add(package)
        
        session.commit()


class OrderService:
    """Service for order management operations"""
    
    @staticmethod
    def create_order(
        session: Session,
        user_id: int,
        package_tier: PackageTier
    ) -> Dict[str, Any]:
        """Create a new order with Razorpay"""
        # Get package
        package = session.exec(select(Package).where(Package.tier == package_tier)).first()
        if not package:
            raise ValueError("Package not found")
        
        # Create Razorpay order
        receipt = f"order_{user_id}_{int(datetime.utcnow().timestamp())}"
        razorpay_order = razorpay_service.create_order(
            amount=package.final_price,
            receipt=receipt
        )
        
        # Create order in database
        order = Order(
            user_id=user_id,
            package_id=package.id,
            razorpay_order_id=razorpay_order["id"],
            amount=package.final_price,
            status=OrderStatus.PENDING
        )
        
        session.add(order)
        session.commit()
        session.refresh(order)
        
        return {
            "order_id": razorpay_order["id"],
            "amount": package.final_price,
            "currency": "INR",
            "key": razorpay_service.client.auth[0],  # Razorpay key ID
            "package_tier": package_tier,
            "package_name": package.name
        }
    
    @staticmethod
    def verify_and_complete_order(
        session: Session,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> Dict[str, Any]:
        """Verify payment and complete order"""
        # Verify signature
        if not razorpay_service.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            raise ValueError("Invalid payment signature")
        
        # Get order
        order = session.exec(
            select(Order).where(Order.razorpay_order_id == razorpay_order_id)
        ).first()
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status == OrderStatus.COMPLETED:
            raise ValueError("Order already completed")
        
        # Update order
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.utcnow()
        
        # Update user package
        UserService.update_user_package(
            session, order.user_id, order.package.tier
        )
        
        # Calculate and create commissions
        user = session.exec(select(User).where(User.id == order.user_id)).first()
        if user and user.referrer_id:
            # Get referrer and their referrer
            referrer = session.exec(select(User).where(User.id == user.referrer_id)).first()
            indirect_referrer_id = referrer.referrer_id if referrer else None
            
            # Calculate commissions
            commissions_data = commission_calculator.calculate_commissions(
                order.package, user.referrer_id, indirect_referrer_id
            )
            
            # Create commission records
            for comm_data in commissions_data:
                commission = Commission(
                    earner_id=comm_data["earner_id"],
                    order_id=order.id,
                    level=comm_data["level"],
                    amount=comm_data["amount"]
                )
                session.add(commission)
        
        session.add(order)
        session.commit()
        
        return {
            "message": "Payment verified successfully",
            "order_id": order.id,
            "status": order.status
        }


class DashboardService:
    """Service for dashboard data operations"""
    
    @staticmethod
    def get_user_stats(session: Session, user_id: int) -> Dict[str, Any]:
        """Get user dashboard statistics"""
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise ValueError("User not found")
        
        # Get earnings
        commissions = session.exec(
            select(Commission).where(Commission.earner_id == user_id)
        ).all()
        
        total_earned = sum(c.amount for c in commissions)
        total_paid_out = sum(c.amount for c in commissions if c.paid_out)
        available_balance = total_earned - total_paid_out
        
        direct_earnings = sum(c.amount for c in commissions if c.level == 1)
        indirect_earnings = sum(c.amount for c in commissions if c.level == 2)
        
        # Get referrals
        direct_referrals = session.exec(
            select(User).where(User.referrer_id == user_id)
        ).all()
        
        indirect_referrals = []
        for referral in direct_referrals:
            indirect_refs = session.exec(
                select(User).where(User.referrer_id == referral.id)
            ).all()
            indirect_referrals.extend(indirect_refs)
        
        return {
            "user": user,
            "earnings": {
                "total_earned": total_earned,
                "total_paid_out": total_paid_out,
                "available_balance": available_balance,
                "direct_earnings": direct_earnings,
                "indirect_earnings": indirect_earnings,
                "total_commissions": len(commissions)
            },
            "referrals": {
                "direct_count": len(direct_referrals),
                "indirect_count": len(indirect_referrals),
                "total_count": len(direct_referrals) + len(indirect_referrals)
            }
        }
    
    @staticmethod
    def get_user_commissions(session: Session, user_id: int) -> List[Commission]:
        """Get user's commission history"""
        return session.exec(
            select(Commission).where(Commission.earner_id == user_id)
        ).all()
    
    @staticmethod
    def get_user_referrals(session: Session, user_id: int) -> Dict[str, List[User]]:
        """Get user's referral network"""
        direct_referrals = session.exec(
            select(User).where(User.referrer_id == user_id)
        ).all()
        
        indirect_referrals = []
        for referral in direct_referrals:
            indirect_refs = session.exec(
                select(User).where(User.referrer_id == referral.id)
            ).all()
            indirect_referrals.extend(indirect_refs)
        
        return {
            "direct_referrals": direct_referrals,
            "indirect_referrals": indirect_referrals
        }