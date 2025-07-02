from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.database import Base
from app.models import * 
# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_online() -> None:
    """A new, simplified 'online' mode to force commit."""
    
    # Create a new, simple engine that points directly to our database
    engine = create_engine("postgresql://user:password@db/task_queue")

    # Use the engine to connect and automatically handle transactions
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        
        # Use the connection's transaction to run the migrations
        with context.begin_transaction():
            context.run_migrations()

# We only need the online mode for this project
run_migrations_online()