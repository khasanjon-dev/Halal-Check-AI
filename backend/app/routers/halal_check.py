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

router = APIRouter(prefix="/halal-check", tags=["halal-check"])


# Allowed image MIME types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
]


async def get_or_create_user(device_id: str, db: AsyncSession) -> User:
    """Get existing user or create new one based on device_id"""
    # Check if user exists
    stmt = select(User).where(User.device_id == device_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        # Create new user
        user = User(device_id=device_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


def normalize_halal_status(is_halal) -> str:
    """Normalize is_halal value to string format"""
    if isinstance(is_halal, bool):
        return "true" if is_halal else "false"
    elif isinstance(is_halal, str):
        # Ensure it's lowercase
        return is_halal.lower()
    else:
        return "doubtful"


def normalize_edible_status(is_edible) -> bool:
    """Normalize is_edible value to boolean format"""
    if isinstance(is_edible, bool):
        return is_edible
    elif isinstance(is_edible, str):
        return is_edible.lower() in ["true", "yes", "1"]
    else:
        return False


@router.post(
    "/analyze",
    response_model=HalalCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze product for halal compliance",
    description="""
Analyze a product description or ingredient list for halal compliance and food safety.

**Parameters:**
- `text`: Product description or ingredient list to analyze
- `device_id`: Unique device identifier

**Returns:**
- Complete halal analysis with reasoning
- Product safety information
- Detected ingredients and allergens
- Analysis is saved to history for the device
""",
)
async def analyze_product(
    request: HalalCheckRequest, db: AsyncSession = Depends(get_db_session)
):
    """Analyze product for halal compliance using Gemini AI"""
    try:
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product text cannot be empty",
            )

        # Get or create user
        user = await get_or_create_user(request.device_id, db)

        # Get Gemini service and analyze
        gemini_service = get_gemini_service()
        analysis_result = await gemini_service.analyze_product(request.text)

        # Normalize the response values
        is_halal_str = normalize_halal_status(analysis_result["is_halal"])
        is_edible_bool = normalize_edible_status(analysis_result["is_edible"])

        # Update analysis_result with normalized values
        analysis_result["is_halal"] = is_halal_str
        analysis_result["is_edible"] = is_edible_bool

        # Save to database
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

        # Prepare response
        return HalalCheckResponse(
            id=product_check.id,
            device_id=product_check.device_id,
            product_name=product_check.product_name,
            is_halal=product_check.is_halal,
            is_edible=product_check.is_edible,
            result=HalalCheckResult(**analysis_result),
            created_at=product_check.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import logging

        logging.error(f"Error analyzing product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing product: {str(e)}",
        )


@router.post(
    "/analyze-image",
    response_model=HalalCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze product image for halal compliance",
    description="""
Analyze a product label image for halal compliance and food safety using OCR.

**Parameters:**
- `image`: Product label image file (JPEG, PNG, GIF, WEBP)
- `device_id`: Unique device identifier

**Returns:**
- Complete halal analysis with reasoning
- OCR-extracted text and ingredients
- Product safety information
- Detected allergens
- Analysis is saved to history for the device

**Supported formats:** JPEG, PNG, GIF, WEBP
**Max size:** 10MB
""",
)
async def analyze_product_image(
    image: UploadFile = File(..., description="Product label image"),
    device_id: str = Form(..., description="Unique device identifier"),
    db: AsyncSession = Depends(get_db_session),
):
    """Analyze product image for halal compliance using Gemini AI with OCR"""
    try:
        # Validate device_id
        if not device_id or not device_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device ID cannot be empty",
            )

        # Validate file type
        content_type = image.content_type
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {content_type}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        # Read image bytes
        image_bytes = await image.read()

        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image file"
            )

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image too large. Maximum size: 10MB, got: {len(image_bytes) / 1024 / 1024:.2f}MB",
            )

        # Get or create user
        user = await get_or_create_user(device_id, db)

        # Get Gemini service and analyze image
        gemini_service = get_gemini_service()
        analysis_result = await gemini_service.analyze_image(image_bytes, content_type)

        # Normalize the response values
        is_halal_str = normalize_halal_status(analysis_result["is_halal"])
        is_edible_bool = normalize_edible_status(analysis_result["is_edible"])

        # Update analysis_result with normalized values
        analysis_result["is_halal"] = is_halal_str
        analysis_result["is_edible"] = is_edible_bool

        # Save to database
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

        # Prepare response
        return HalalCheckResponse(
            id=product_check.id,
            device_id=product_check.device_id,
            product_name=product_check.product_name,
            is_halal=product_check.is_halal,
            is_edible=product_check.is_edible,
            result=HalalCheckResult(**analysis_result),
            created_at=product_check.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import logging

        logging.error(f"Error analyzing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}",
        )


@router.get(
    "/history/{device_id}",
    response_model=List[ProductCheckHistory],
    status_code=status.HTTP_200_OK,
    summary="Get product check history",
    description="""
Get the product check history for a specific device.

**Parameters:**
- `device_id`: Unique device identifier
- `limit`: Maximum number of records to return (default: 50, max: 100)

**Returns:**
- List of previous product checks ordered by most recent first
""",
)
async def get_history(
    device_id: str, limit: int = 50, db: AsyncSession = Depends(get_db_session)
):
    """Get product check history for a device"""
    try:
        # Validate limit
        if limit < 1:
            limit = 50
        elif limit > 100:
            limit = 100

        # Get user
        stmt = select(User).where(User.device_id == device_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return []

        # Get product checks
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
                id=check.id,
                product_name=check.product_name,
                is_halal=check.is_halal,
                is_edible=check.is_edible,
                created_at=check.created_at.isoformat(),
            )
            for check in checks
        ]

    except Exception as e:
        import logging

        logging.error(f"Error fetching history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}",
        )


@router.get(
    "/check/{check_id}",
    response_model=HalalCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Get specific product check details",
    description="""
Get detailed information about a specific product check.

**Parameters:**
- `check_id`: The ID of the product check

**Returns:**
- Complete product check details including full analysis
""",
)
async def get_check_details(check_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get details of a specific product check"""
    try:
        stmt = select(ProductCheck).where(ProductCheck.id == check_id)
        result = await db.execute(stmt)
        check = result.scalar_one_or_none()

        if check is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product check not found"
            )

        return HalalCheckResponse(
            id=check.id,
            device_id=check.device_id,
            product_name=check.product_name,
            is_halal=check.is_halal,
            is_edible=check.is_edible,
            result=HalalCheckResult(**check.result_json),
            created_at=check.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging

        logging.error(f"Error fetching check details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching check details: {str(e)}",
        )
