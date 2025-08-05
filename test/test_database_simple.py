"""Simple database tests to verify basic functionality."""

from __future__ import annotations

from src.db.database import DatabaseManager
from src.db.models import User


def test_simple_database_operations() -> None:
    """Test basic database operations."""
    # Create in-memory database
    db_manager = DatabaseManager("sqlite:///:memory:")

    # Create tables
    db_manager.create_tables()

    # Create a user
    user = User(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )

    # Add to database
    with db_manager.client.get_session() as session:
        session.add(user)
        session.commit()
        session.refresh(user)

        # Verify user was created
        assert user.id is not None
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"

        # Get user by ID
        retrieved_user = session.get(User, user.id)
        assert retrieved_user is not None
        assert retrieved_user.first_name == "John"

        # Get user by email
        from sqlmodel import select

        statement = select(User).where(User.email == "john.doe@example.com")
        user_by_email = session.exec(statement).first()
        assert user_by_email is not None
        assert user_by_email.id == user.id


def test_database_count() -> None:
    """Test database count operations."""
    db_manager = DatabaseManager("sqlite:///:memory:")
    db_manager.create_tables()

    # Should be empty initially
    assert db_manager.users.count() == 0

    # Create a user
    user = User(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )

    with db_manager.client.get_session() as session:
        session.add(user)
        session.commit()

    # Should have one user now
    assert db_manager.users.count() == 1


if __name__ == "__main__":
    test_simple_database_operations()
    test_database_count()
    print("All simple database tests passed!")
