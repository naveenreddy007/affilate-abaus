from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PackageTier(str, Enum):
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    is_active: bool = Field(default=True)
    
    # Referral system
    referrer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    referrer: Optional["User"] = Relationship(back_populates="referrals", sa_relationship_kwargs={"remote_side": "User.id"})
    referrals: List["User"] = Relationship(back_populates="referrer")
    
    # Package information
    package_tier: Optional[PackageTier] = Field(default=None)
    purchased_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="user")
    earned_commissions: List["Commission"] = Relationship(back_populates="earner")


class Package(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tier: PackageTier = Field(unique=True)
    name: str
    description: Optional[str] = Field(default=None)
    base_price: int  # Price in paise (₹29.99 = 2999 paise)
    gst_rate: float = Field(default=18.0)  # GST percentage
    
    # Commission structure
    direct_commission: int  # Commission in paise
    indirect_commission: int  # Commission in paise
    
    # Features
    features: str = Field(default="[]")  # JSON string of features
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="package")
    
    @property
    def gst_amount(self) -> int:
        """Calculate GST amount in paise"""
        return int(self.base_price * (self.gst_rate / 100))
    
    @property
    def final_price(self) -> int:
        """Calculate final price including GST in paise"""
        return self.base_price + self.gst_amount


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(default=None)
    video_url: Optional[str] = Field(default=None)
    thumbnail_url: Optional[str] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None)
    
    # Access control
    required_package: Optional[PackageTier] = Field(default=None)
    is_free: bool = Field(default=True)
    
    # SEO
    slug: str = Field(unique=True, index=True)
    meta_description: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User and package
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="orders")
    
    package_id: int = Field(foreign_key="package.id")
    package: Package = Relationship(back_populates="orders")
    
    # Payment details
    razorpay_order_id: str = Field(unique=True, index=True)
    razorpay_payment_id: Optional[str] = Field(default=None)
    razorpay_signature: Optional[str] = Field(default=None)
    
    # Order details
    amount: int  # Amount in paise
    currency: str = Field(default="INR")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    commissions: List["Commission"] = Relationship(back_populates="order")


class Commission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Who earned the commission
    earner_id: int = Field(foreign_key="user.id")
    earner: User = Relationship(back_populates="earned_commissions")
    
    # Which order generated the commission
    order_id: int = Field(foreign_key="order.id")
    order: Order = Relationship(back_populates="commissions")
    
    # Commission details
    level: int = Field(description="1 for direct, 2 for indirect")
    amount: int  # Commission amount in paise
    
    # Payout status
    paid_out: bool = Field(default=False)
    paid_out_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Payout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User receiving payout
    user_id: int = Field(foreign_key="user.id")
    
    # Payout details
    amount: int  # Amount in paise
    commission_ids: str  # JSON array of commission IDs
    
    # Payment details
    payment_method: str = Field(default="bank_transfer")
    transaction_id: Optional[str] = Field(default=None)
    status: str = Field(default="pending")  # pending, completed, failed
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)