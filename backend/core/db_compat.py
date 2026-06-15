"""Database compatibility layer.
Makes SQLAlchemy models work with both SQLite (free, no server) and PostgreSQL.
SQLite doesn't support: UUID, JSONB, ARRAY, ENUM natively.
This module provides fallback types."""

from sqlalchemy import TypeDecorator, String, Text, JSON
from core.config import settings
import uuid
import json

_use_sqlite = "sqlite" in settings.DATABASE_URL


class UUIDType(TypeDecorator):
    """UUID type that works with both SQLite and PostgreSQL."""
    impl = String if _use_sqlite else String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value) if isinstance(value, str) else value


class JSONType(TypeDecorator):
    """JSON type that works with both SQLite and PostgreSQL.
    In SQLite: stores as Text. In Postgres: uses native JSON."""
    impl = Text if _use_sqlite else String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
