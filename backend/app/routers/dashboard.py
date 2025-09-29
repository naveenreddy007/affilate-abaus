from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from ..database import get_session
from ..models import User, Commission
from ..auth import get_current_active_user
from ..services import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class EarningsStats(BaseModel):
    total_earned: int
    total_paid_out: int
    available_balance: int
    direct_earnings: int
    indirect_earnings: int
    total_commissions: int


class ReferralStats(BaseModel):
    direct_count: int
    indirect_count: int
    total_count: int


class UserInfo(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    referrer_id: int | None
    package_tier: str | None
    purchased_at: str | None
    created_at: str


class DashboardStatsResponse(BaseModel):
    user: UserInfo
    earnings: EarningsStats
    referrals: ReferralStats


class CommissionResponse(BaseModel):
    id: int
    level: int
    amount: int
    paid_out: bool
    created_at: str
    paid_out_at: str | None
    order_id: int


class ReferralUser(BaseModel):
    id: int
    email: str
    full_name: str
    package_tier: str | None
    purchased_at: str | None
    created_at: str


class ReferralsResponse(BaseModel):
    direct_referrals: List[ReferralUser]
    indirect_referrals: List[ReferralUser]


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get user dashboard statistics"""
    stats = DashboardService.get_user_stats(session, current_user.id)
    
    user_info = UserInfo(
        id=stats["user"].id,
        email=stats["user"].email,
        full_name=stats["user"].full_name,
        is_active=stats["user"].is_active,
        referrer_id=stats["user"].referrer_id,
        package_tier=stats["user"].package_tier,
        purchased_at=stats["user"].purchased_at.isoformat() if stats["user"].purchased_at else None,
        created_at=stats["user"].created_at.isoformat()
    )
    
    earnings = EarningsStats(**stats["earnings"])
    referrals = ReferralStats(**stats["referrals"])
    
    return DashboardStatsResponse(
        user=user_info,
        earnings=earnings,
        referrals=referrals
    )


@router.get("/commissions", response_model=List[CommissionResponse])
async def get_commissions(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get user's commission history"""
    commissions = DashboardService.get_user_commissions(session, current_user.id)
    
    commission_responses = []
    for commission in commissions:
        commission_responses.append(CommissionResponse(
            id=commission.id,
            level=commission.level,
            amount=commission.amount,
            paid_out=commission.paid_out,
            created_at=commission.created_at.isoformat(),
            paid_out_at=commission.paid_out_at.isoformat() if commission.paid_out_at else None,
            order_id=commission.order_id
        ))
    
    return commission_responses


@router.get("/referrals", response_model=ReferralsResponse)
async def get_referrals(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get user's referral network"""
    referrals_data = DashboardService.get_user_referrals(session, current_user.id)
    
    def user_to_referral_user(user: User) -> ReferralUser:
        return ReferralUser(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            package_tier=user.package_tier,
            purchased_at=user.purchased_at.isoformat() if user.purchased_at else None,
            created_at=user.created_at.isoformat()
        )
    
    direct_referrals = [user_to_referral_user(user) for user in referrals_data["direct_referrals"]]
    indirect_referrals = [user_to_referral_user(user) for user in referrals_data["indirect_referrals"]]
    
    return ReferralsResponse(
        direct_referrals=direct_referrals,
        indirect_referrals=indirect_referrals
    )