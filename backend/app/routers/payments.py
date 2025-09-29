from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from ..database import get_session
from ..models import User, PackageTier
from ..auth import get_current_active_user
from ..services import OrderService

router = APIRouter(prefix="/payments", tags=["payments"])


class CreateOrderRequest(BaseModel):
    package_tier: PackageTier


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key: str
    package_tier: str
    package_name: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    message: str
    order_id: int
    status: str


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a Razorpay order for package purchase"""
    try:
        order_data = OrderService.create_order(
            session=session,
            user_id=current_user.id,
            package_tier=request.package_tier
        )
        
        return CreateOrderResponse(**order_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-payment", response_model=VerifyPaymentResponse)
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Verify Razorpay payment and complete order"""
    try:
        result = OrderService.verify_and_complete_order(
            session=session,
            razorpay_order_id=request.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
        
        return VerifyPaymentResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )