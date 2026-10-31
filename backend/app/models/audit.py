from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import (
    ForeignKey,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import (
    Base,
    BigIntFK,
    BigIntPK,
    UTCDateTime,
    get_utc_now,
)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(
        BigIntFK, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[int | None] = mapped_column(BigIntFK, nullable=True, index=True)
    before_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    after_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=get_utc_now, nullable=False, index=True
    )

    # Relationships
    actor_user = relationship("User", foreign_keys=[actor_user_id])
