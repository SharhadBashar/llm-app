'''
    Alembic migration environment for the AI service.
    Only touches objects in the `ai` schema.
'''

from __future__ import annotations

import sys
from typing import Any
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

# ---------------------------------------------------------------------------
# 1. Add project root to PYTHONPATH so imports work when Alembic runs
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# 2. Load env vars & core DB config
# ---------------------------------------------------------------------------
from dotenv import load_dotenv  # type: ignore

load_dotenv(PROJECT_ROOT / '.env')           # adjust if you use .env.local etc.

from db import Base, DATABASE_URL       # noqa: E402  (after sys.path tweak)
import core  # noqa: F401, E402

# ---------------------------------------------------------------------------
# 3. Alembic Config
# ---------------------------------------------------------------------------
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Inject the runtime URL so alembic.ini can stay generic
config.set_main_option('sqlalchemy.url', DATABASE_URL)

target_metadata = Base.metadata
AI_SCHEMA = 'ai'

# ---------------------------------------------------------------------------
# 4. Filter: only keep objects that live in the `ai` schema
# ---------------------------------------------------------------------------
def include_object(
    obj: Any, name: str, type_: str, reflected: bool, compare_to: Any
) -> bool:
    '''
        Skip anything outside the `ai` schema during autogenerate.
        - Tables / indexes / constraints carry .schema
        - Enums come through as `type_ == "type"`
    '''
    if hasattr(obj, 'schema'):
        return obj.schema == AI_SCHEMA

    if (type_ == 'type'):                    # enum, domain, etc.
        # For model-declared enums, reflected is False
        return not reflected

    return True


# ---------------------------------------------------------------------------
# 5. Migration helpers
# ---------------------------------------------------------------------------
def _configure_context(**kwargs):
    '''
        Common configure arguments shared by offline/online modes.
    '''
    context.configure(
        target_metadata = target_metadata,
        include_schemas = True,
        version_table_schema = AI_SCHEMA,
        include_object = include_object,
        compare_type = True,     # detect column type changes
        compare_server_default = True,
        **kwargs,
    )


def run_migrations_offline() -> None:
    url = config.get_main_option('sqlalchemy.url')
    _configure_context(
        url = url,
        literal_binds = True,
        dialect_opts = {'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix = 'sqlalchemy.',
        poolclass = pool.NullPool,
    )

    with connectable.connect() as connection:
        # Bootstrap the ai schema so Alembic can store alembic_version there
        connection.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{AI_SCHEMA}"')
        connection.commit() # so the transaction closes immediately

        _configure_context(connection=connection)

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# 6. Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
