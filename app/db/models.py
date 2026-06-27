from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
	display_name: Mapped[str] = mapped_column(String(120), nullable=False)
	telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	alert_preferences: Mapped[list["AlertPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")


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

	user: Mapped[User] = relationship(back_populates="alert_preferences")


class ParsedListing(Base):
	__tablename__ = "parsed_listings"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	source_channel: Mapped[str] = mapped_column(String(255), nullable=False)
	raw_text: Mapped[str] = mapped_column(String, nullable=False)
	venue: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
	listing_date: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
	start_time: Mapped[time] = mapped_column(Time, nullable=False)
	end_time: Mapped[time] = mapped_column(Time, nullable=False)
	price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class TelegramMessage(Base):
    __tablename__ = "telegram_messages"

    id = mapped_column(Integer, primary_key=True)

    telegram_chat_id = mapped_column(BigInteger, nullable=False)
    telegram_message_id = mapped_column(Integer, nullable=False)
    telegram_topic_id = mapped_column(Integer, nullable=True)

    sender_id = mapped_column(BigInteger, nullable=True)
    text = mapped_column(Text, nullable=False)
    message_date = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "telegram_chat_id",
            "telegram_message_id",
            name="uq_telegram_chat_message",
        ),
    )

class CourtTransfer(Base):
    __tablename__ = "court_transfers"

    id = mapped_column(Integer, primary_key=True)

    fingerprint = mapped_column(String, nullable=False, unique=True, index=True)

    seller_id = mapped_column(BigInteger, nullable=True, index=True)

    intent = mapped_column(String, nullable=False)
    venue = mapped_column(String, nullable=True)
    date = mapped_column(Date, nullable=True)
    start_time = mapped_column(Time, nullable=True)
    end_time = mapped_column(Time, nullable=True)
    court_number = mapped_column(String, nullable=True)
    price = mapped_column(Numeric, nullable=True)

    status = mapped_column(String, nullable=False, default="active")
