from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Define the SQLModel for the 'users' table
class User(SQLModel, table=True, table_name="users"):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    user_status: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    password_hash: bytes
    password_salt: bytes
    n_samples_collected: int = Field(default=0)

# Create a SQLite engine for demonstration purposes
engine = create_engine("postgresql://postgres:root@172.25.0.10:5432/postgres")

# Create a session
with Session(engine) as session:
    users = session.exec(select(User)).all()
    for user in users:
        print(f"User ID: {user.user_id}, Username: {user.user_name}, Status: {user.user_status}")