from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db_session
from app.models.halal_check import User, ProductCheck
from app.schemas.halal_check import (
    HalalCheckRequest,
    HalalCheckResponse,
    HalalCheckResult,
    ProductCheckHistory,
)
from app.utils.gemini import get_gemini_service
from app.utils.helpers import patch_analysis_result, normalize_halal_status, normalize_edible_status

router = APIRouter(prefix="/halal-check", tags=["halal-check"])

ALLOWED_IMAGE_TYPES = [
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
]


async def get_or_create_user(device_id: str, db: AsyncSession) -> User:
    """Fetch existing user by device_id or create a new one."""
    stmt = select(User).where(User.device_id == device_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(device_id=device_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/analyze", response_model=HalalCheckResponse, status_code=status.HTTP_200_OK)
async def analyze_product(
        request: HalalCheckRequest,
        db: AsyncSession = Depends(get_db_session),
):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Product text cannot be empty")

    user = await get_or_create_user(request.device_id, db)
    gemini = get_gemini_service()
    analysis_result = await gemini.analyze_product(request.text)

    analysis_result = patch_analysis_result(analysis_result, request.text)

    is_halal_str = normalize_halal_status(analysis_result["is_halal"])
    is_edible_bool = normalize_edible_status(analysis_result["is_edible"])
    analysis_result["is_halal"] = is_halal_str
    analysis_result["is_edible"] = is_edible_bool

    product_check = ProductCheck(
        user_id=user.id,
        device_id=request.device_id,
        product_name=analysis_result["product_name"],
        is_halal=is_halal_str,
        is_edible=is_edible_bool,
        result_json=analysis_result,
        input_text=request.text,
    )
    db.add(product_check)
    await db.commit()
    await db.refresh(product_check)

    return HalalCheckResponse(
        id=product_check.id,
        device_id=product_check.device_id,
        product_name=product_check.product_name,
        is_halal=product_check.is_halal,
        is_edible=product_check.is_edible,
        result=HalalCheckResult(**analysis_result),
        created_at=product_check.created_at.isoformat(),
    )


@router.post("/analyze-image", response_model=HalalCheckResponse)
async def analyze_product_image(
        image: UploadFile = File(...),
        device_id: str = Form(...),
        db: AsyncSession = Depends(get_db_session),
):
    if not device_id or not device_id.strip():
        raise HTTPException(status_code=400, detail="Device ID cannot be empty")
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {image.content_type}")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    user = await get_or_create_user(device_id, db)
    gemini = get_gemini_service()
    analysis_result = await gemini.analyze_image(image_bytes, image.content_type)

    analysis_result = patch_analysis_result(analysis_result, image.filename or "Image Product")
    is_halal_str = normalize_halal_status(analysis_result["is_halal"])
    is_edible_bool = normalize_edible_status(analysis_result["is_edible"])
    analysis_result["is_halal"] = is_halal_str
    analysis_result["is_edible"] = is_edible_bool

    product_check = ProductCheck(
        user_id=user.id,
        device_id=device_id,
        product_name=analysis_result["product_name"],
        is_halal=is_halal_str,
        is_edible=is_edible_bool,
        result_json=analysis_result,
        input_text=f"Image: {image.filename}",
    )
    db.add(product_check)
    await db.commit()
    await db.refresh(product_check)

    return HalalCheckResponse(
        id=product_check.id,
        device_id=product_check.device_id,
        product_name=product_check.product_name,
        is_halal=product_check.is_halal,
        is_edible=product_check.is_edible,
        result=HalalCheckResult(**analysis_result),
        created_at=product_check.created_at.isoformat(),
    )


@router.get("/history/{device_id}", response_model=List[ProductCheckHistory])
async def get_history(device_id: str, limit: int = 50, db: AsyncSession = Depends(get_db_session)):
    limit = max(1, min(limit, 100))
    stmt = select(User).where(User.device_id == device_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return []

    stmt = (
        select(ProductCheck)
        .where(ProductCheck.user_id == user.id)
        .order_by(desc(ProductCheck.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    checks = result.scalars().all()

    return [
        ProductCheckHistory(
            id=c.id,
            product_name=c.product_name,
            is_halal=c.is_halal,
            is_edible=c.is_edible,
            created_at=c.created_at.isoformat(),
        )
        for c in checks
    ]


@router.get("/check/{check_id}", response_model=HalalCheckResponse)
async def get_check_details(check_id: int, db: AsyncSession = Depends(get_db_session)):
    stmt = select(ProductCheck).where(ProductCheck.id == check_id)
    result = await db.execute(stmt)
    check = result.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=404, detail="Not found")
    return HalalCheckResponse(
        id=check.id,
        device_id=check.device_id,
        product_name=check.product_name,
        is_halal=check.is_halal,
        is_edible=check.is_edible,
        result=HalalCheckResult(**check.result_json),
        created_at=check.created_at.isoformat(),
    )
