from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlertPreference(Base):
    __tablename__ = "alert_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    earliest_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    latest_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    max_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="alert_preferences")
