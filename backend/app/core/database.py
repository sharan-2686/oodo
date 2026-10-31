from collections.abc import Generator
from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    Numeric,
    create_engine,
)
from sqlalchemy.dialects.mysql import (
    BIGINT as MYSQL_BIGINT,
    DATETIME as MYSQL_DATETIME,
    DECIMAL as MYSQL_DECIMAL,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Engine configuration
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # MySQL InnoDB production-grade connection pool settings
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "pool_size": 10,
            "max_overflow": 20,
        }
    )

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2 models."""
    pass


# Dialect-adaptive column types for MySQL & SQLite compatibility
BigIntPK = BigInteger().with_variant(
    MYSQL_BIGINT(unsigned=True), "mysql"
).with_variant(Integer, "sqlite")
PK_BIGINT = BigIntPK

BigIntFK = BigInteger().with_variant(
    MYSQL_BIGINT(unsigned=True), "mysql"
).with_variant(Integer, "sqlite")

MoneyAmount = Numeric(12, 2).with_variant(
    MYSQL_DECIMAL(12, 2), "mysql"
)

QuantityAmount = Numeric(12, 3).with_variant(
    MYSQL_DECIMAL(12, 3), "mysql"
)

TaxRatePercent = Numeric(7, 4).with_variant(
    MYSQL_DECIMAL(7, 4), "mysql"
)

UTCDateTime = DateTime(timezone=False).with_variant(
    MYSQL_DATETIME(fsp=6), "mysql"
)


def get_utc_now() -> datetime:
    """Return timezone-naive UTC timestamp for MySQL compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

