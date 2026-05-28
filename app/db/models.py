from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(32), nullable=False, default="draft")
    reward_pool_gold = Column(Integer, nullable=False, default=0)
    reward_pool_diamond = Column(Integer, nullable=False, default=0)
    drop_item_id = Column(String(128), nullable=False)
    drop_probability = Column(Float, nullable=False)
    daily_limit = Column(Integer, nullable=False)
    pity_threshold = Column(Integer, nullable=True)
    risk_level = Column(String(32), nullable=False, default="low")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        CheckConstraint(
            "status in ('draft', 'published', 'rolled_back')",
            name="ck_activity_status",
        ),
    )

    reward_records = relationship("RewardRecord", back_populates="activity")


class UserWallet(Base):
    __tablename__ = "user_wallets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(128), nullable=False, unique=True, index=True)
    gold = Column(Integer, nullable=False, default=0)
    diamond = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class RewardRecord(Base):
    __tablename__ = "reward_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(128), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False, unique=True, index=True)
    reward_gold = Column(Integer, nullable=False, default=0)
    reward_diamond = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="success")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    activity = relationship("Activity", back_populates="reward_records")


class AgentReviewRecord(Base):
    __tablename__ = "agent_review_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    review_id = Column(String(128), nullable=False, unique=True, index=True)
    status = Column(String(32), nullable=False, default="pending", index=True)
    reason = Column(String(512), nullable=False)
    config_json = Column(Text, nullable=False)
    probability_result_json = Column(Text, nullable=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    reviewed_at = Column(DateTime, nullable=True)

    activity = relationship("Activity")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trace_id = Column(String(128), nullable=True, index=True)
    actor = Column(String(128), nullable=False, default="system", index=True)
    operation_type = Column(String(128), nullable=False, index=True)
    target_type = Column(String(128), nullable=False, index=True)
    target_id = Column(String(128), nullable=True, index=True)
    request_json = Column(Text, nullable=True)
    response_json = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="success", index=True)
    message = Column(String(512), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
