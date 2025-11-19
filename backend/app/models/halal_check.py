from typing import Optional
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import mapped_column, Mapped

from app.utils.database import BaseDB, BaseTimeStamp


class User(BaseDB, BaseTimeStamp):
    """User model based on device ID"""
    device_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)


class ProductCheck(BaseDB, BaseTimeStamp):
    """Product check model for storing halal analysis results"""
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_halal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "true", "false", "doubtful"
    is_edible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    input_text: Mapped[str] = mapped_column(String, nullable=False)

