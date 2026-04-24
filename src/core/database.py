from sqlmodel import Session, create_engine

# SQLite configuration
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# WAL mode makes SQLite concurrent and fast
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session():
    """FastAPI dependency to inject the database session."""
    with Session(engine) as session:
        yield session
