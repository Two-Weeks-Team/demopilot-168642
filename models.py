import os
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    create_engine,
    inspect,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ---------------------------------------------------------------------------
# Database URL handling (env var conversion & SSL settings)
# ---------------------------------------------------------------------------
_raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if _raw_url.startswith("postgresql+asyncpg://"):
    _raw_url = _raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql+psycopg://")

# Add SSL mode for remote Postgres instances (non‑localhost & non‑sqlite)
if (
    not _raw_url.startswith("sqlite")
    and "localhost" not in _raw_url
    and "127.0.0.1" not in _raw_url
    and "sslmode=" not in _raw_url.lower()
):
    if "?" in _raw_url:
        _raw_url = f"{_raw_url}&sslmode=require"
    else:
        _raw_url = f"{_raw_url}?sslmode=require"

engine = create_engine(_raw_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ---------------------------------------------------------------------------
# Table name prefix – prevents collisions in shared DBs
# ---------------------------------------------------------------------------
PREFIX = "dp_"

# ---------------------------------------------------------------------------
# SQLAlchemy models (synchronous)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = f"{PREFIX}users"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    demos = relationship("Demo", back_populates="owner")
    rehearsals = relationship("Rehearsal", back_populates="owner")
    feedbacks = relationship("Feedback", back_populates="owner")
    scripts = relationship("Script", back_populates="owner")

class Demo(Base):
    __tablename__ = f"{PREFIX}demos"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    beats = Column(JSON, nullable=False)  # [{"section":..., "content":...}, ...]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="demos")
    rehearsals = relationship("Rehearsal", back_populates="demo")

class Rehearsal(Base):
    __tablename__ = f"{PREFIX}rehearsals"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}users.id"), nullable=False)
    demo_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}demos.id"), nullable=False)
    recording_url = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="rehearsals")
    demo = relationship("Demo", back_populates="rehearsals")
    feedbacks = relationship("Feedback", back_populates="rehearsal")
    script = relationship("Script", uselist=False, back_populates="rehearsal")

class Feedback(Base):
    __tablename__ = f"{PREFIX}feedback"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}users.id"), nullable=False)
    rehearsal_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}rehearsals.id"), nullable=False)
    payload = Column(JSON, nullable=False)  # full AI response JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="feedbacks")
    rehearsal = relationship("Rehearsal", back_populates="feedbacks")

class Script(Base):
    __tablename__ = f"{PREFIX}scripts"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}users.id"), nullable=False)
    rehearsal_id = Column(PGUUID(as_uuid=True), ForeignKey(f"{PREFIX}rehearsals.id"), nullable=True)
    content = Column(JSON, nullable=False)  # generated script & key points
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="scripts")
    rehearsal = relationship("Rehearsal", back_populates="script")

# Create tables if they do not exist (useful for the demo environment)
if not inspect(engine).has_table(User.__tablename__):
    Base.metadata.create_all(bind=engine)
