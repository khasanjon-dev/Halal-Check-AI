import logging
import typing as t
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

class_registry: t.Dict = {}

logger = logging.getLogger(__name__)


@as_declarative(class_registry=class_registry)
class BaseDB:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class BaseTimeStamp:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=True,
    )

    def __str__(self):
        return f"{self.id}"
