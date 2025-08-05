"""Database layer for SQLModel-based persistence.

This module provides a centralized database client and repository pattern
for performing CRUD operations on the application's data models.
"""

from __future__ import annotations

import contextlib
from typing import Generator, Generic, TypeVar

from loguru import logger
from sqlmodel import Session, SQLModel, create_engine, select

from src.config import SETTINGS

from .models import (
    CandidateResponse,
    Certification,
    Comment,
    Company,
    Education,
    Experience,
    JobPosting,
    User,
)

# Type variable for SQLModel classes
T = TypeVar("T", bound=SQLModel)


class DatabaseClient:
    """Centralized database client for managing connections and sessions."""

    def __init__(self, database_url: str | None = None) -> None:
        """Initialize the database client.

        Args:
            database_url: Database URL. Defaults to settings database_url.
        """
        self.database_url = database_url or SETTINGS.database_url
        self.engine = create_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
        )

    def create_tables(self) -> None:
        """Create all database tables."""
        SQLModel.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")

    def drop_tables(self) -> None:
        """Drop all database tables."""
        SQLModel.metadata.drop_all(self.engine)
        logger.info("Database tables dropped successfully")

    @contextlib.contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session context manager.

        Yields:
            Database session
        """
        with Session(self.engine, expire_on_commit=False) as session:
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                logger.exception(f"Database session error: {e}")
                raise
            finally:
                session.close()

    def get_session_keep_alive(self) -> Session:
        """Get a database session that stays alive for manual management.

        Returns:
            Database session
        """
        return Session(self.engine, expire_on_commit=False)


class Repository(Generic[T]):
    """Generic repository pattern for CRUD operations."""

    def __init__(self, model: type[T], db_client: DatabaseClient) -> None:
        """Initialize the repository.

        Args:
            model: The SQLModel class to operate on
            db_client: Database client instance
        """
        self.model = model
        self.db_client = db_client

    def create(self, obj: T) -> T:
        """Create a new object in the database.

        Args:
            obj: The object to create

        Returns:
            The created object with updated ID
        """
        with self.db_client.get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            # Get a fresh copy of the object to avoid detached instance issues
            result = session.get(self.model, obj.id)
            logger.debug(f"Created {self.model.__name__} with ID: {obj.id}")
            return result

    def get_by_id(self, obj_id: int) -> T | None:
        """Get an object by its ID.

        Args:
            obj_id: The object's ID

        Returns:
            The object if found, None otherwise
        """
        with self.db_client.get_session() as session:
            return session.get(self.model, obj_id)

    def get_all(self, limit: int | None = None, offset: int = 0) -> list[T]:
        """Get all objects with optional pagination.

        Args:
            limit: Maximum number of objects to return
            offset: Number of objects to skip

        Returns:
            List of objects
        """
        with self.db_client.get_session() as session:
            statement = select(self.model).offset(offset)
            if limit:
                statement = statement.limit(limit)
            return list(session.exec(statement))

    def update(self, obj: T) -> T:
        """Update an existing object.

        Args:
            obj: The object to update

        Returns:
            The updated object
        """
        with self.db_client.get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            logger.debug(f"Updated {self.model.__name__} with ID: {obj.id}")
            return obj

    def delete(self, obj_id: int) -> bool:
        """Delete an object by its ID.

        Args:
            obj_id: The object's ID

        Returns:
            True if deleted, False if not found
        """
        with self.db_client.get_session() as session:
            obj = session.get(self.model, obj_id)
            if obj:
                session.delete(obj)
                session.commit()
                logger.debug(f"Deleted {self.model.__name__} with ID: {obj_id}")
                return True
            return False

    def count(self) -> int:
        """Get the total count of objects.

        Returns:
            Total count
        """
        with self.db_client.get_session() as session:
            return len(list(session.exec(select(self.model))))


class UserRepository(Repository[User]):
    """Repository for User operations."""

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email.

        Args:
            email: The user's email address

        Returns:
            The user if found, None otherwise
        """
        with self.db_client.get_session() as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()


class EducationRepository(Repository[Education]):
    """Repository for Education operations."""

    def get_by_user_id(self, user_id: int) -> list[Education]:
        """Get all education records for a user.

        Args:
            user_id: The user's ID

        Returns:
            List of education records
        """
        with self.db_client.get_session() as session:
            statement = select(Education).where(Education.user_id == user_id)
            return list(session.exec(statement))


class CertificationRepository(Repository[Certification]):
    """Repository for Certification operations."""

    def get_by_user_id(self, user_id: int) -> list[Certification]:
        """Get all certification records for a user.

        Args:
            user_id: The user's ID

        Returns:
            List of certification records
        """
        with self.db_client.get_session() as session:
            statement = select(Certification).where(Certification.user_id == user_id)
            return list(session.exec(statement))


class ExperienceRepository(Repository[Experience]):
    """Repository for Experience operations."""

    def get_by_user_id(self, user_id: int) -> list[Experience]:
        """Get all experience records for a user.

        Args:
            user_id: The user's ID

        Returns:
            List of experience records
        """
        with self.db_client.get_session() as session:
            statement = select(Experience).where(Experience.user_id == user_id)
            return list(session.exec(statement))


class CompanyRepository(Repository[Company]):
    """Repository for Company operations."""

    def get_by_name(self, name: str) -> Company | None:
        """Get a company by name.

        Args:
            name: The company name

        Returns:
            The company if found, None otherwise
        """
        with self.db_client.get_session() as session:
            statement = select(Company).where(Company.name == name)
            return session.exec(statement).first()


class JobPostingRepository(Repository[JobPosting]):
    """Repository for JobPosting operations."""

    def get_by_company_id(self, company_id: int) -> list[JobPosting]:
        """Get all job postings for a company.

        Args:
            company_id: The company's ID

        Returns:
            List of job postings
        """
        with self.db_client.get_session() as session:
            statement = select(JobPosting).where(JobPosting.company_id == company_id)
            return list(session.exec(statement))


class CommentRepository(Repository[Comment]):
    """Repository for Comment operations."""

    def get_by_job_posting_id(self, job_posting_id: int) -> list[Comment]:
        """Get all comments for a job posting.

        Args:
            job_posting_id: The job posting's ID

        Returns:
            List of comments
        """
        with self.db_client.get_session() as session:
            statement = select(Comment).where(Comment.job_posting_id == job_posting_id)
            return list(session.exec(statement))

    def get_by_company_id(self, company_id: int) -> list[Comment]:
        """Get all comments for a company.

        Args:
            company_id: The company's ID

        Returns:
            List of comments
        """
        with self.db_client.get_session() as session:
            statement = select(Comment).where(Comment.company_id == company_id)
            return list(session.exec(statement))


class CandidateResponseRepository(Repository[CandidateResponse]):
    """Repository for CandidateResponse operations."""

    def get_by_user_id(self, user_id: int) -> list[CandidateResponse]:
        """Get all candidate responses for a user.

        Args:
            user_id: The user's ID

        Returns:
            List of candidate responses
        """
        with self.db_client.get_session() as session:
            statement = select(CandidateResponse).where(CandidateResponse.user_id == user_id)
            return list(session.exec(statement))


class DatabaseManager:
    """Centralized database manager providing access to all repositories."""

    def __init__(self, database_url: str | None = None) -> None:
        """Initialize the database manager.

        Args:
            database_url: Database URL. Defaults to settings database_url.
        """
        self.client = DatabaseClient(database_url)

        # Initialize repositories
        self.users = UserRepository(User, self.client)
        self.educations = EducationRepository(Education, self.client)
        self.certifications = CertificationRepository(Certification, self.client)
        self.experiences = ExperienceRepository(Experience, self.client)
        self.companies = CompanyRepository(Company, self.client)
        self.job_postings = JobPostingRepository(JobPosting, self.client)
        self.comments = CommentRepository(Comment, self.client)
        self.candidate_responses = CandidateResponseRepository(CandidateResponse, self.client)

    def create_tables(self) -> None:
        """Create all database tables."""
        self.client.create_tables()

    def drop_tables(self) -> None:
        """Drop all database tables."""
        self.client.drop_tables()

    def get_session(self) -> Session:
        """Get a database session.

        Returns:
            Database session
        """
        return self.client.get_session()


# Global database manager instance
db_manager = DatabaseManager()
