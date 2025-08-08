"""Tests for resume data adapter functions."""

from datetime import date

import pytest
from src.db.database import DatabaseManager
from src.db.models import CandidateResponse, Certification, Education, Experience, User
from src.features.resume.data_adapter import (
    detect_missing_optional_data,
    detect_missing_required_data,
    fetch_candidate_responses,
    fetch_experience_data,
    fetch_user_data,
    transform_user_to_resume_data,
)


class TestDataAdapter:
    """Test cases for data adapter functions."""

    @pytest.fixture
    def db_manager(self) -> DatabaseManager:
        """Create a test database manager."""
        return DatabaseManager("sqlite:///:memory:")

    def test_fetch_user_data_success(self, db_manager):
        """Test successful user data fetching."""
        db_manager.create_tables()

        # Create test user
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555)-123-4567",
            linkedin_url="https://linkedin.com/in/johndoe",
        )
        created_user = db_manager.users.create(user)

        # Create test education
        education = Education(
            user_id=created_user.id,
            degree="Bachelor of Science",
            major="Computer Science",
            institution="University of Example",
            grad_date=date(2020, 5, 15),
        )
        db_manager.educations.create(education)

        # Create test certification
        certification = Certification(
            user_id=created_user.id,
            title="AWS Certified Solutions Architect",
            date=date(2021, 6, 20),
        )
        db_manager.certifications.create(certification)

        # Test fetch_user_data
        result = fetch_user_data(created_user.id, db_manager)

        assert result["user"] == created_user
        assert len(result["education"]) == 1
        assert result["education"][0].degree == "Bachelor of Science"
        assert len(result["certifications"]) == 1
        assert result["certifications"][0].title == "AWS Certified Solutions Architect"

    def test_fetch_user_data_user_not_found(self, db_manager):
        """Test user data fetching with non-existent user."""
        with pytest.raises(ValueError, match="User with ID 999 not found"):
            fetch_user_data(999)

    def test_fetch_experience_data(self, db_manager):
        """Test experience data fetching."""
        db_manager.create_tables()

        # Create test user
        user = User(first_name="Jane", last_name="Smith", email="jane@example.com")
        created_user = db_manager.users.create(user)

        # Create test experiences
        exp1 = Experience(
            user_id=created_user.id,
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            content="Developed web applications using Python and React.",
        )
        exp2 = Experience(
            user_id=created_user.id,
            title="Senior Developer",
            company="Startup Inc",
            location="Remote",
            start_date=date(2023, 1, 1),
            end_date=None,
            content="Led development team and implemented new features.",
        )
        db_manager.experiences.create(exp1)
        db_manager.experiences.create(exp2)

        # Test fetch_experience_data
        result = fetch_experience_data(created_user.id, db_manager)

        assert len(result) == 2
        assert any(exp.title == "Software Engineer" for exp in result)
        assert any(exp.title == "Senior Developer" for exp in result)

    def test_fetch_candidate_responses(self, db_manager):
        """Test candidate responses fetching."""
        db_manager.create_tables()

        # Create test user
        user = User(first_name="Bob", last_name="Johnson", email="bob@example.com")
        created_user = db_manager.users.create(user)

        # Create test responses
        resp1 = CandidateResponse(
            user_id=created_user.id,
            prompt="What are your strengths?",
            response="I am detail-oriented and have strong problem-solving skills.",
        )
        resp2 = CandidateResponse(
            user_id=created_user.id,
            prompt="Describe a challenging project.",
            response="I led a team to develop a complex web application.",
        )
        db_manager.candidate_responses.create(resp1)
        db_manager.candidate_responses.create(resp2)

        # Test fetch_candidate_responses
        result = fetch_candidate_responses(created_user.id, db_manager)

        assert len(result) == 2
        assert any(resp.prompt == "What are your strengths?" for resp in result)
        assert any(resp.prompt == "Describe a challenging project." for resp in result)

    def test_transform_user_to_resume_data(self, db_manager):
        """Test user data transformation to ResumeData."""
        db_manager.create_tables()

        # Create test user
        user = User(
            first_name="Alice",
            last_name="Brown",
            email="alice@example.com",
            phone="555-123-4567",
            linkedin_url="https://linkedin.com/in/alicebrown",
        )
        created_user = db_manager.users.create(user)

        # Create test education
        education = Education(
            user_id=created_user.id,
            degree="Master of Science",
            major="Data Science",
            institution="Data University",
            grad_date=date(2021, 8, 20),
        )
        db_manager.educations.create(education)

        # Create test experience
        experience = Experience(
            user_id=created_user.id,
            title="Data Scientist",
            company="Analytics Corp",
            location="New York, NY",
            start_date=date(2021, 9, 1),
            end_date=None,
            content="Developed machine learning models for customer segmentation.",
        )
        db_manager.experiences.create(experience)

        # Create test response
        response = CandidateResponse(
            user_id=created_user.id,
            prompt="What are your career goals?",
            response="I want to become a senior data scientist and lead ML projects.",
        )
        db_manager.candidate_responses.create(response)

        # Test transformation
        user_data = fetch_user_data(created_user.id, db_manager)
        experience_data = fetch_experience_data(created_user.id, db_manager)
        responses = fetch_candidate_responses(created_user.id, db_manager)

        resume_data = transform_user_to_resume_data(
            user_data, experience_data, responses, "Senior Data Scientist"
        )

        assert resume_data.name == "Alice Brown"
        assert resume_data.title == "Senior Data Scientist"
        assert resume_data.email == "alice@example.com"
        assert resume_data.phone == "(555)-123-4567"
        assert resume_data.linkedin_url == "https://linkedin.com/in/alicebrown"
        assert len(resume_data.education) == 1
        assert resume_data.education[0].degree == "Master of Science"
        assert len(resume_data.experience) == 1
        assert resume_data.experience[0].title == "Data Scientist"
        assert resume_data.experience[0].end_date == "Present"

    def test_transform_user_to_resume_data_missing_required_fields(self, db_manager):
        """Test transformation with missing required fields."""
        db_manager.create_tables()

        # Create user with missing required fields
        user = User(first_name="", last_name="", email="")
        created_user = db_manager.users.create(user)

        user_data = fetch_user_data(created_user.id, db_manager)
        experience_data = fetch_experience_data(created_user.id, db_manager)
        responses = fetch_candidate_responses(created_user.id, db_manager)

        with pytest.raises(ValueError, match="User must have first and last name"):
            transform_user_to_resume_data(user_data, experience_data, responses, "Developer")

    def test_detect_missing_required_data(self, db_manager):
        """Test detection of missing required data."""
        db_manager.create_tables()

        # Create user with missing fields
        user = User(first_name="", last_name="Doe", email="")
        created_user = db_manager.users.create(user)

        user_data = fetch_user_data(created_user.id, db_manager)
        missing_fields = detect_missing_required_data(user_data)

        assert "first_name" in missing_fields
        assert "email" in missing_fields
        assert "last_name" not in missing_fields

    def test_detect_missing_optional_data(self, db_manager):
        """Test detection of missing optional data."""
        db_manager.create_tables()

        # Create user with minimal data
        user = User(first_name="John", last_name="Doe", email="john@example.com")
        created_user = db_manager.users.create(user)

        user_data = fetch_user_data(created_user.id, db_manager)
        experience_data = fetch_experience_data(created_user.id, db_manager)
        responses = fetch_candidate_responses(created_user.id, db_manager)

        missing_fields = detect_missing_optional_data(user_data, experience_data, responses)

        assert "phone" in missing_fields
        assert "linkedin_url" in missing_fields
        assert "education" in missing_fields
        assert "experience" in missing_fields
        assert "candidate_responses" in missing_fields
