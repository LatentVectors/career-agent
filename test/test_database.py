"""Tests for database functionality."""

from __future__ import annotations

import datetime

import pytest
from src.db.database import DatabaseManager
from src.db.models import (
    CandidateResponse,
    Certification,
    Comment,
    Company,
    Education,
    Experience,
    JobPosting,
    User,
)


class TestDatabase:
    """Test database functionality."""

    @pytest.fixture
    def db_manager(self) -> DatabaseManager:
        """Create a test database manager."""
        return DatabaseManager("sqlite:///:memory:")

    def test_create_tables(self, db_manager: DatabaseManager) -> None:
        """Test that tables can be created."""
        db_manager.create_tables()
        # Should not raise an exception

    def test_user_profile_crud(self, db_manager: DatabaseManager) -> None:
        """Test user profile CRUD operations."""
        db_manager.create_tables()

        # Create user profile
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555)-123-4567",
            linkedin_url="https://linkedin.com/in/johndoe",
        )

        created_user = db_manager.users.create(user)
        assert created_user.id is not None
        assert created_user.first_name == "John"
        assert created_user.last_name == "Doe"
        assert created_user.email == "john.doe@example.com"

        # Get user by ID
        retrieved_user = db_manager.users.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.first_name == "John"

        # Get user by email
        user_by_email = db_manager.users.get_by_email("john.doe@example.com")
        assert user_by_email is not None
        assert user_by_email.id == created_user.id

        # Update user
        retrieved_user.first_name = "Jane"
        updated_user = db_manager.users.update(retrieved_user)
        assert updated_user.first_name == "Jane"

        # Delete user
        deleted = db_manager.users.delete(created_user.id)
        assert deleted is True

        # Verify deletion
        deleted_user = db_manager.users.get_by_id(created_user.id)
        assert deleted_user is None

    def test_experience_crud(self, db_manager: DatabaseManager) -> None:
        """Test experience CRUD operations."""
        db_manager.create_tables()

        # Create user first
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        created_user = db_manager.users.create(user)

        # Create experience
        experience = Experience(
            user_id=created_user.id,
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            start_date=datetime.date(2020, 1, 1),
            end_date=datetime.date(2023, 12, 31),
            content="Developed web applications using Python and React.",
        )

        created_exp = db_manager.experiences.create(experience)
        assert created_exp.id is not None
        assert created_exp.title == "Software Engineer"
        assert created_exp.company == "Tech Corp"

        # Get experiences by user
        user_experiences = db_manager.experiences.get_by_user_id(created_user.id)
        assert len(user_experiences) == 1
        assert user_experiences[0].title == "Software Engineer"

    def test_company_and_job_crud(self, db_manager: DatabaseManager) -> None:
        """Test company and job posting CRUD operations."""
        db_manager.create_tables()

        # Create company
        company = Company(
            name="Tech Corp",
            website="https://techcorp.com",
            email="jobs@techcorp.com",
            overview="Leading technology company",
        )

        created_company = db_manager.companies.create(company)
        assert created_company.id is not None
        assert created_company.name == "Tech Corp"

        # Create job posting
        import json

        job = JobPosting(
            company_id=created_company.id,
            description="Senior Software Engineer position",
            requirements=json.dumps({1: "Python", 2: "React", 3: "5+ years experience"}),
            keywords=json.dumps({"python": 5, "react": 3, "javascript": 2}),
        )

        created_job = db_manager.job_postings.create(job)
        assert created_job.id is not None
        assert created_job.description == "Senior Software Engineer position"

        # Get jobs by company
        company_jobs = db_manager.job_postings.get_by_company_id(created_company.id)
        assert len(company_jobs) == 1
        assert company_jobs[0].description == "Senior Software Engineer position"

    def test_comment_crud(self, db_manager: DatabaseManager) -> None:
        """Test comment CRUD operations."""
        db_manager.create_tables()

        # Create company and job
        company = Company(name="Tech Corp")
        created_company = db_manager.companies.create(company)

        job = JobPosting(
            company_id=created_company.id,
            description="Software Engineer",
        )
        created_job = db_manager.job_postings.create(job)

        # Create comment for job
        job_comment = Comment(
            text="Great opportunity for growth",
            job_posting_id=created_job.id,
        )

        created_job_comment = db_manager.comments.create(job_comment)
        assert created_job_comment.id is not None
        assert created_job_comment.text == "Great opportunity for growth"

        # Create comment for company
        company_comment = Comment(
            text="Excellent company culture",
            company_id=created_company.id,
        )

        created_company_comment = db_manager.comments.create(company_comment)
        assert created_company_comment.id is not None
        assert created_company_comment.text == "Excellent company culture"

        # Get comments by job
        job_comments = db_manager.comments.get_by_job_posting_id(created_job.id)
        assert len(job_comments) == 1
        assert job_comments[0].text == "Great opportunity for growth"

        # Get comments by company
        company_comments = db_manager.comments.get_by_company_id(created_company.id)
        assert len(company_comments) == 1
        assert company_comments[0].text == "Excellent company culture"

    def test_education_and_certification_crud(self, db_manager: DatabaseManager) -> None:
        """Test education and certification CRUD operations."""
        db_manager.create_tables()

        # Create user
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        created_user = db_manager.users.create(user)

        # Create education
        education = Education(
            user_id=created_user.id,
            degree="Bachelor of Science",
            major="Computer Science",
            institution="University of Technology",
            grad_date=datetime.date(2020, 5, 15),
        )

        created_education = db_manager.educations.create(education)
        assert created_education.id is not None
        assert created_education.degree == "Bachelor of Science"

        # Create certification
        certification = Certification(
            user_id=created_user.id,
            title="AWS Certified Solutions Architect",
            date=datetime.date(2022, 6, 1),
        )

        created_certification = db_manager.certifications.create(certification)
        assert created_certification.id is not None
        assert created_certification.title == "AWS Certified Solutions Architect"

        # Get user's education and certifications
        user_educations = db_manager.educations.get_by_user_id(created_user.id)
        assert len(user_educations) == 1
        assert user_educations[0].degree == "Bachelor of Science"

        user_certifications = db_manager.certifications.get_by_user_id(created_user.id)
        assert len(user_certifications) == 1
        assert user_certifications[0].title == "AWS Certified Solutions Architect"

    def test_candidate_response_crud(self, db_manager: DatabaseManager) -> None:
        """Test candidate response CRUD operations."""
        db_manager.create_tables()

        # Create user
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        created_user = db_manager.users.create(user)

        # Create candidate response
        response = CandidateResponse(
            user_id=created_user.id,
            prompt="What are your career goals?",
            response="I want to become a senior software engineer and lead development teams.",
        )

        created_response = db_manager.candidate_responses.create(response)
        assert created_response.id is not None
        assert created_response.prompt == "What are your career goals?"
        assert "senior software engineer" in created_response.response

        # Get user's responses
        user_responses = db_manager.candidate_responses.get_by_user_id(created_user.id)
        assert len(user_responses) == 1
        assert user_responses[0].prompt == "What are your career goals?"
