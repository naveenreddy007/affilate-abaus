from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from pydantic import BaseModel
import json

from ..database import get_session
from ..models import Package
from ..services import PackageService

router = APIRouter(prefix="/packages", tags=["packages"])


class PackageResponse(BaseModel):
    id: int
    tier: str
    name: str
    description: str
    base_price: int
    gst_amount: int
    final_price: int
    direct_commission: int
    indirect_commission: int
    features: List[str]
    created_at: str


@router.get("/", response_model=List[PackageResponse])
async def get_packages(session: Session = Depends(get_session)):
    """Get all available packages"""
    packages = PackageService.get_all_packages(session)
    
    package_responses = []
    for package in packages:
        try:
            features = json.loads(package.features)
        except (json.JSONDecodeError, TypeError):
            features = []
        
        package_responses.append(PackageResponse(
            id=package.id,
            tier=package.tier,
            name=package.name,
            description=package.description or "",
            base_price=package.base_price,
            gst_amount=package.gst_amount,
            final_price=package.final_price,
            direct_commission=package.direct_commission,
            indirect_commission=package.indirect_commission,
            features=features,
            created_at=package.created_at.isoformat()
        ))
    
    return package_responses