"""Database CLI commands.

This module provides comprehensive CLI commands for database operations including
CRUD operations for all database models and database management commands.
"""

from __future__ import annotations

import datetime

import typer
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table

from .database import db_manager
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

console = Console()

# Create the main database CLI app
db_app = typer.Typer(help="Database management commands")

# Create sub-apps for each model type
user_app = typer.Typer(help="User management commands")
education_app = typer.Typer(help="Education management commands")
certification_app = typer.Typer(help="Certification management commands")
experience_app = typer.Typer(help="Experience management commands")
company_app = typer.Typer(help="Company management commands")
job_posting_app = typer.Typer(help="Job posting management commands")
comment_app = typer.Typer(help="Comment management commands")
candidate_response_app = typer.Typer(help="Candidate response management commands")

# Add sub-apps to main app
db_app.add_typer(user_app, name="user")
db_app.add_typer(education_app, name="education")
db_app.add_typer(certification_app, name="certification")
db_app.add_typer(experience_app, name="experience")
db_app.add_typer(company_app, name="company")
db_app.add_typer(job_posting_app, name="job-posting")
db_app.add_typer(comment_app, name="comment")
db_app.add_typer(candidate_response_app, name="candidate-response")

# ---------------------------------------------------------------------------
# Database management commands
# ---------------------------------------------------------------------------


@db_app.command("reset")
def db_reset() -> None:
    """Reset the database by dropping and recreating all tables."""
    if typer.confirm("This will delete ALL data in the database. Are you sure?"):
        db_manager.drop_tables()
        db_manager.create_tables()
        typer.echo("Database reset successfully.")


@db_app.command("status")
def db_status() -> None:
    """Show database status and record counts."""
    table = Table(title="Database Status")
    table.add_column("Table", style="cyan")
    table.add_column("Record Count", style="magenta")

    # Count records for each model
    counts = {
        "Users": db_manager.users.count(),
        "Education": db_manager.educations.count(),
        "Certifications": db_manager.certifications.count(),
        "Experience": db_manager.experiences.count(),
        "Companies": db_manager.companies.count(),
        "Job Postings": db_manager.job_postings.count(),
        "Comments": db_manager.comments.count(),
        "Candidate Responses": db_manager.candidate_responses.count(),
    }

    for table_name, count in counts.items():
        table.add_row(table_name, str(count))

    console.print(table)


# ---------------------------------------------------------------------------
# User commands
# ---------------------------------------------------------------------------


@user_app.command("list")
def user_list() -> None:
    """List all users."""
    users = db_manager.users.get_all()

    if not users:
        typer.echo("No users found.")
        return

    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")
    table.add_column("Phone", style="yellow")
    table.add_column("Created", style="blue")

    for user in users:
        table.add_row(
            str(user.id),
            user.full_name,
            user.email or "-",
            user.phone or "-",
            user.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@user_app.command("show")
def user_show(user_id: int) -> None:
    """Show detailed information for a specific user."""
    user = db_manager.users.get_by_id(user_id)

    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    # Get related data
    education = db_manager.educations.get_by_user_id(user_id)
    certifications = db_manager.certifications.get_by_user_id(user_id)
    experience = db_manager.experiences.get_by_user_id(user_id)
    responses = db_manager.candidate_responses.get_by_user_id(user_id)

    console.print("\n[bold cyan]User Details[/bold cyan]")
    pprint(user.model_dump())

    if education:
        console.print(f"\n[bold green]Education ({len(education)} records)[/bold green]")
        for edu in education:
            pprint(edu.model_dump())

    if certifications:
        console.print(
            f"\n[bold yellow]Certifications ({len(certifications)} records)[/bold yellow]"
        )
        for cert in certifications:
            pprint(cert.model_dump())

    if experience:
        console.print(f"\n[bold magenta]Experience ({len(experience)} records)[/bold magenta]")
        for exp in experience:
            pprint(exp.model_dump())

    if responses:
        console.print(f"\n[bold blue]Candidate Responses ({len(responses)} records)[/bold blue]")
        for resp in responses:
            pprint(resp.model_dump())


@user_app.command("create")
def user_create(
    first_name: str = typer.Option(..., prompt=True),
    last_name: str = typer.Option(..., prompt=True),
    email: str = typer.Option(None, prompt=True),
    phone: str = typer.Option(None, prompt=True),
    linkedin_url: str = typer.Option(None, prompt=True),
) -> None:
    """Create a new user."""
    # Check if email is already taken
    if email and db_manager.users.get_by_email(email):
        typer.echo(f"User with email {email} already exists.")
        raise typer.Exit(code=1)

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        linkedin_url=linkedin_url,
    )

    created_user = db_manager.users.create(user)
    typer.echo(f"User created with ID: {created_user.id}")
    # Get the user again to avoid detached instance issues
    user_data = db_manager.users.get_by_id(created_user.id)
    if user_data:
        typer.echo(
            f"User details: {user_data.first_name} {user_data.last_name} ({user_data.email})"
        )


@user_app.command("update")
def user_update(
    user_id: int = typer.Option(..., "--user-id"),
    first_name: str = typer.Option(None),
    last_name: str = typer.Option(None),
    email: str = typer.Option(None),
    phone: str = typer.Option(None),
    linkedin_url: str = typer.Option(None),
) -> None:
    """Update an existing user."""
    user = db_manager.users.get_by_id(user_id)

    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if email is not None:
        # Check if email is already taken by another user
        existing_user = db_manager.users.get_by_email(email)
        if existing_user and existing_user.id != user_id:
            typer.echo(f"User with email {email} already exists.")
            raise typer.Exit(code=1)
        user.email = email
    if phone is not None:
        user.phone = phone
    if linkedin_url is not None:
        user.linkedin_url = linkedin_url

    user.updated_at = datetime.datetime.now()
    db_manager.users.update(user)
    typer.echo(f"User {user_id} updated successfully.")


@user_app.command("delete")
def user_delete(user_id: int) -> None:
    """Delete a user and all associated data."""
    user = db_manager.users.get_by_id(user_id)

    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(f"Delete user '{user.full_name}' and all associated data?"):
        # Delete associated data first
        education = db_manager.educations.get_by_user_id(user_id)
        for edu in education:
            db_manager.educations.delete(edu.id)

        certifications = db_manager.certifications.get_by_user_id(user_id)
        for cert in certifications:
            db_manager.certifications.delete(cert.id)

        experience = db_manager.experiences.get_by_user_id(user_id)
        for exp in experience:
            db_manager.experiences.delete(exp.id)

        responses = db_manager.candidate_responses.get_by_user_id(user_id)
        for resp in responses:
            db_manager.candidate_responses.delete(resp.id)

        # Delete the user
        db_manager.users.delete(user_id)
        typer.echo(f"User {user_id} and all associated data deleted successfully.")


# ---------------------------------------------------------------------------
# Education commands
# ---------------------------------------------------------------------------


@education_app.command("list")
def education_list(user_id: int | None = typer.Option(None, "--user-id")) -> None:
    """List education records."""
    if user_id:
        education = db_manager.educations.get_by_user_id(user_id)
    else:
        education = db_manager.educations.get_all()

    if not education:
        typer.echo("No education records found.")
        return

    table = Table(title="Education Records")
    table.add_column("ID", style="cyan")
    table.add_column("User ID", style="magenta")
    table.add_column("Degree", style="green")
    table.add_column("Major", style="yellow")
    table.add_column("Institution", style="blue")
    table.add_column("Graduation Date", style="red")

    for edu in education:
        table.add_row(
            str(edu.id),
            str(edu.user_id),
            edu.degree,
            edu.major,
            edu.institution,
            edu.grad_date.strftime("%Y-%m"),
        )

    console.print(table)


@education_app.command("create")
def education_create(
    user_id: int = typer.Option(..., prompt=True),
    degree: str = typer.Option(..., prompt=True),
    major: str = typer.Option(..., prompt=True),
    institution: str = typer.Option(..., prompt=True),
    grad_date: str = typer.Option(..., prompt=True, help="Graduation date, e.g. 2024-05"),
) -> None:
    """Create a new education record."""
    # Verify user exists
    user = db_manager.users.get_by_id(user_id)
    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    # Parse the graduation date
    try:
        parsed_date = datetime.datetime.strptime(grad_date, "%Y-%m").date()
    except ValueError:
        typer.echo("Invalid date format. Please use YYYY-MM format (e.g., 2024-05).")
        raise typer.Exit(code=1)

    education = Education(
        user_id=user_id,
        degree=degree,
        major=major,
        institution=institution,
        grad_date=parsed_date,
    )

    created_education = db_manager.educations.create(education)
    typer.echo(f"Education record created with ID: {created_education.id}")


@education_app.command("show")
def education_show(education_id: int) -> None:
    """Show detailed information for a specific education record."""
    education = db_manager.educations.get_by_id(education_id)

    if education is None:
        typer.echo(f"No education record found with ID {education_id}.")
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]Education Details[/bold cyan]")
    pprint(education.model_dump())


@education_app.command("update")
def education_update(
    education_id: int = typer.Option(..., "--education-id"),
    degree: str = typer.Option(None),
    major: str = typer.Option(None),
    institution: str = typer.Option(None),
    grad_date: str = typer.Option(None, help="Graduation date, e.g. 2024-05"),
) -> None:
    """Update an existing education record."""
    education = db_manager.educations.get_by_id(education_id)

    if education is None:
        typer.echo(f"No education record found with ID {education_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if degree is not None:
        education.degree = degree
    if major is not None:
        education.major = major
    if institution is not None:
        education.institution = institution
    if grad_date is not None:
        try:
            parsed_date = datetime.datetime.strptime(grad_date, "%Y-%m").date()
            education.grad_date = parsed_date
        except ValueError:
            typer.echo("Invalid date format. Please use YYYY-MM format (e.g., 2024-05).")
            raise typer.Exit(code=1)

    education.updated_at = datetime.datetime.now()
    db_manager.educations.update(education)
    typer.echo(f"Education record {education_id} updated successfully.")


@education_app.command("delete")
def education_delete(education_id: int) -> None:
    """Delete an education record."""
    education = db_manager.educations.get_by_id(education_id)

    if education is None:
        typer.echo(f"No education record found with ID {education_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(
        f"Delete education record for {education.degree} at {education.institution}?"
    ):
        db_manager.educations.delete(education_id)
        typer.echo(f"Education record {education_id} deleted successfully.")


# ---------------------------------------------------------------------------
# Certification commands
# ---------------------------------------------------------------------------


@certification_app.command("list")
def certification_list(user_id: int | None = typer.Option(None, "--user-id")) -> None:
    """List certification records."""
    if user_id:
        certifications = db_manager.certifications.get_by_user_id(user_id)
    else:
        certifications = db_manager.certifications.get_all()

    if not certifications:
        typer.echo("No certification records found.")
        return

    table = Table(title="Certification Records")
    table.add_column("ID", style="cyan")
    table.add_column("User ID", style="magenta")
    table.add_column("Title", style="green")
    table.add_column("Date Obtained", style="yellow")

    for cert in certifications:
        table.add_row(
            str(cert.id),
            str(cert.user_id),
            cert.title,
            cert.date.strftime("%Y-%m"),
        )

    console.print(table)


@certification_app.command("create")
def certification_create(
    user_id: int = typer.Option(..., prompt=True),
    title: str = typer.Option(..., prompt=True),
    date: str = typer.Option(..., prompt=True, help="Date obtained, e.g. 2023-11"),
) -> None:
    """Create a new certification record."""
    # Verify user exists
    user = db_manager.users.get_by_id(user_id)
    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    # Parse the certification date
    try:
        parsed_date = datetime.datetime.strptime(date, "%Y-%m").date()
    except ValueError:
        typer.echo("Invalid date format. Please use YYYY-MM format (e.g., 2023-11).")
        raise typer.Exit(code=1)

    certification = Certification(
        user_id=user_id,
        title=title,
        date=parsed_date,
    )

    created_certification = db_manager.certifications.create(certification)
    typer.echo(f"Certification record created with ID: {created_certification.id}")


@certification_app.command("show")
def certification_show(certification_id: int) -> None:
    """Show detailed information for a specific certification record."""
    certification = db_manager.certifications.get_by_id(certification_id)

    if certification is None:
        typer.echo(f"No certification record found with ID {certification_id}.")
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]Certification Details[/bold cyan]")
    pprint(certification.model_dump())


@certification_app.command("update")
def certification_update(
    certification_id: int = typer.Option(..., "--certification-id"),
    title: str = typer.Option(None),
    date: str = typer.Option(None, help="Date obtained, e.g. 2023-11"),
) -> None:
    """Update an existing certification record."""
    certification = db_manager.certifications.get_by_id(certification_id)

    if certification is None:
        typer.echo(f"No certification record found with ID {certification_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if title is not None:
        certification.title = title
    if date is not None:
        try:
            parsed_date = datetime.datetime.strptime(date, "%Y-%m").date()
            certification.date = parsed_date
        except ValueError:
            typer.echo("Invalid date format. Please use YYYY-MM format (e.g., 2023-11).")
            raise typer.Exit(code=1)

    certification.updated_at = datetime.datetime.now()
    db_manager.certifications.update(certification)
    typer.echo(f"Certification record {certification_id} updated successfully.")


@certification_app.command("delete")
def certification_delete(certification_id: int) -> None:
    """Delete a certification record."""
    certification = db_manager.certifications.get_by_id(certification_id)

    if certification is None:
        typer.echo(f"No certification record found with ID {certification_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(f"Delete certification record for '{certification.title}'?"):
        db_manager.certifications.delete(certification_id)
        typer.echo(f"Certification record {certification_id} deleted successfully.")


# ---------------------------------------------------------------------------
# Experience commands
# ---------------------------------------------------------------------------


@experience_app.command("list")
def experience_list(user_id: int | None = typer.Option(None, "--user-id")) -> None:
    """List experience records."""
    if user_id:
        experiences = db_manager.experiences.get_by_user_id(user_id)
    else:
        experiences = db_manager.experiences.get_all()

    if not experiences:
        typer.echo("No experience records found.")
        return

    table = Table(title="Experience Records")
    table.add_column("ID", style="cyan")
    table.add_column("User ID", style="magenta")
    table.add_column("Title", style="green")
    table.add_column("Company", style="yellow")
    table.add_column("Location", style="blue")
    table.add_column("Duration", style="red")

    for exp in experiences:
        duration = f"{exp.start_date.strftime('%Y-%m')} - "
        if exp.end_date:
            duration += exp.end_date.strftime("%Y-%m")
        else:
            duration += "Present"

        table.add_row(
            str(exp.id),
            str(exp.user_id),
            exp.title,
            exp.company,
            exp.location,
            duration,
        )

    console.print(table)


@experience_app.command("create")
def experience_create(
    user_id: int = typer.Option(..., prompt=True),
    title: str = typer.Option(..., prompt=True),
    company: str = typer.Option(..., prompt=True),
    location: str = typer.Option(..., prompt=True),
    start_date: str = typer.Option(..., prompt=True, help="Start date, e.g. 2023-01"),
    end_date: str = typer.Option(
        None, prompt=True, help="End date, e.g. 2024-01 (or leave empty for current)"
    ),
    content: str = typer.Option(
        ..., prompt=True, help="Detailed description of your role and achievements"
    ),
) -> None:
    """Create a new experience record."""
    # Verify user exists
    user = db_manager.users.get_by_id(user_id)
    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    # Parse the start date
    try:
        parsed_start_date = datetime.datetime.strptime(start_date, "%Y-%m").date()
    except ValueError:
        typer.echo("Invalid start date format. Please use YYYY-MM format (e.g., 2023-01).")
        raise typer.Exit(code=1)

    # Parse the end date if provided
    parsed_end_date = None
    if end_date:
        try:
            parsed_end_date = datetime.datetime.strptime(end_date, "%Y-%m").date()
        except ValueError:
            typer.echo("Invalid end date format. Please use YYYY-MM format (e.g., 2024-01).")
            raise typer.Exit(code=1)

    experience = Experience(
        user_id=user_id,
        title=title,
        company=company,
        location=location,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        content=content,
    )

    created_experience = db_manager.experiences.create(experience)
    typer.echo(f"Experience record created with ID: {created_experience.id}")


@experience_app.command("show")
def experience_show(experience_id: int) -> None:
    """Show detailed information for a specific experience record."""
    experience = db_manager.experiences.get_by_id(experience_id)

    if experience is None:
        typer.echo(f"No experience record found with ID {experience_id}.")
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]Experience Details[/bold cyan]")
    pprint(experience.model_dump())


@experience_app.command("update")
def experience_update(
    experience_id: int = typer.Option(..., "--experience-id"),
    title: str = typer.Option(None),
    company: str = typer.Option(None),
    location: str = typer.Option(None),
    start_date: str = typer.Option(None, help="Start date, e.g. 2023-01"),
    end_date: str = typer.Option(None, help="End date, e.g. 2024-01"),
    content: str = typer.Option(None),
) -> None:
    """Update an existing experience record."""
    experience = db_manager.experiences.get_by_id(experience_id)

    if experience is None:
        typer.echo(f"No experience record found with ID {experience_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if title is not None:
        experience.title = title
    if company is not None:
        experience.company = company
    if location is not None:
        experience.location = location
    if start_date is not None:
        try:
            parsed_start_date = datetime.datetime.strptime(start_date, "%Y-%m").date()
            experience.start_date = parsed_start_date
        except ValueError:
            typer.echo("Invalid start date format. Please use YYYY-MM format (e.g., 2023-01).")
            raise typer.Exit(code=1)
    if end_date is not None:
        try:
            parsed_end_date = datetime.datetime.strptime(end_date, "%Y-%m").date()
            experience.end_date = parsed_end_date
        except ValueError:
            typer.echo("Invalid end date format. Please use YYYY-MM format (e.g., 2024-01).")
            raise typer.Exit(code=1)
    if content is not None:
        experience.content = content

    experience.updated_at = datetime.datetime.now()
    db_manager.experiences.update(experience)
    typer.echo(f"Experience record {experience_id} updated successfully.")


@experience_app.command("delete")
def experience_delete(experience_id: int) -> None:
    """Delete an experience record."""
    experience = db_manager.experiences.get_by_id(experience_id)

    if experience is None:
        typer.echo(f"No experience record found with ID {experience_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(
        f"Delete experience record for '{experience.title}' at {experience.company}?"
    ):
        db_manager.experiences.delete(experience_id)
        typer.echo(f"Experience record {experience_id} deleted successfully.")


# ---------------------------------------------------------------------------
# Company commands
# ---------------------------------------------------------------------------


@company_app.command("list")
def company_list() -> None:
    """List all companies."""
    companies = db_manager.companies.get_all()

    if not companies:
        typer.echo("No companies found.")
        return

    table = Table(title="Companies")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Website", style="green")
    table.add_column("Email", style="yellow")
    table.add_column("Created", style="blue")

    for company in companies:
        table.add_row(
            str(company.id),
            company.name,
            company.website or "-",
            company.email or "-",
            company.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@company_app.command("show")
def company_show(company_id: int) -> None:
    """Show detailed information for a specific company."""
    company = db_manager.companies.get_by_id(company_id)

    if company is None:
        typer.echo(f"No company found with ID {company_id}.")
        raise typer.Exit(code=1)

    # Get related job postings
    job_postings = db_manager.job_postings.get_by_company_id(company_id)
    comments = db_manager.comments.get_by_company_id(company_id)

    console.print("\n[bold cyan]Company Details[/bold cyan]")
    pprint(company.model_dump())

    if job_postings:
        console.print(f"\n[bold green]Job Postings ({len(job_postings)} records)[/bold green]")
        for job in job_postings:
            pprint(job.model_dump())

    if comments:
        console.print(f"\n[bold yellow]Comments ({len(comments)} records)[/bold yellow]")
        for comment in comments:
            pprint(comment.model_dump())


@company_app.command("create")
def company_create(
    name: str = typer.Option(..., prompt=True),
    website: str = typer.Option(None, prompt=True),
    email: str = typer.Option(None, prompt=True),
    overview: str = typer.Option(None, prompt=True),
) -> None:
    """Create a new company."""
    # Check if company already exists
    existing_company = db_manager.companies.get_by_name(name)
    if existing_company:
        typer.echo(f"Company with name '{name}' already exists.")
        raise typer.Exit(code=1)

    company = Company(
        name=name,
        website=website,
        email=email,
        overview=overview,
    )

    created_company = db_manager.companies.create(company)
    typer.echo(f"Company created with ID: {created_company.id}")


@company_app.command("update")
def company_update(
    company_id: int = typer.Option(..., "--company-id"),
    name: str = typer.Option(None),
    website: str = typer.Option(None),
    email: str = typer.Option(None),
    overview: str = typer.Option(None),
) -> None:
    """Update an existing company."""
    company = db_manager.companies.get_by_id(company_id)

    if company is None:
        typer.echo(f"No company found with ID {company_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if name is not None:
        # Check if name is already taken by another company
        existing_company = db_manager.companies.get_by_name(name)
        if existing_company and existing_company.id != company_id:
            typer.echo(f"Company with name '{name}' already exists.")
            raise typer.Exit(code=1)
        company.name = name
    if website is not None:
        company.website = website
    if email is not None:
        company.email = email
    if overview is not None:
        company.overview = overview

    company.updated_at = datetime.datetime.now()
    db_manager.companies.update(company)
    typer.echo(f"Company {company_id} updated successfully.")


@company_app.command("delete")
def company_delete(company_id: int) -> None:
    """Delete a company and all associated data."""
    company = db_manager.companies.get_by_id(company_id)

    if company is None:
        typer.echo(f"No company found with ID {company_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(f"Delete company '{company.name}' and all associated data?"):
        # Delete associated job postings first
        job_postings = db_manager.job_postings.get_by_company_id(company_id)
        for job in job_postings:
            db_manager.job_postings.delete(job.id)

        # Delete associated comments
        comments = db_manager.comments.get_by_company_id(company_id)
        for comment in comments:
            db_manager.comments.delete(comment.id)

        # Delete the company
        db_manager.companies.delete(company_id)
        typer.echo(f"Company {company_id} and all associated data deleted successfully.")


# ---------------------------------------------------------------------------
# Job Posting commands
# ---------------------------------------------------------------------------


@job_posting_app.command("list")
def job_posting_list(company_id: int | None = typer.Option(None, "--company-id")) -> None:
    """List job postings."""
    if company_id:
        job_postings = db_manager.job_postings.get_by_company_id(company_id)
    else:
        job_postings = db_manager.job_postings.get_all()

    if not job_postings:
        typer.echo("No job postings found.")
        return

    table = Table(title="Job Postings")
    table.add_column("ID", style="cyan")
    table.add_column("Company ID", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Requirements", style="yellow")
    table.add_column("Keywords", style="blue")
    table.add_column("Created", style="red")

    for job in job_postings:
        # Get company name
        company = db_manager.companies.get_by_id(job.company_id)
        company_name = company.name if company else f"Company {job.company_id}"

        table.add_row(
            str(job.id),
            company_name,
            job.description[:50] + "..." if len(job.description) > 50 else job.description,
            job.requirements[:30] + "..." if len(job.requirements) > 30 else job.requirements,
            job.keywords[:30] + "..." if len(job.keywords) > 30 else job.keywords,
            job.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@job_posting_app.command("show")
def job_posting_show(job_posting_id: int) -> None:
    """Show detailed information for a specific job posting."""
    job_posting = db_manager.job_postings.get_by_id(job_posting_id)

    if job_posting is None:
        typer.echo(f"No job posting found with ID {job_posting_id}.")
        raise typer.Exit(code=1)

    # Get related comments
    comments = db_manager.comments.get_by_job_posting_id(job_posting_id)

    console.print("\n[bold cyan]Job Posting Details[/bold cyan]")
    pprint(job_posting.model_dump())

    if comments:
        console.print(f"\n[bold green]Comments ({len(comments)} records)[/bold green]")
        for comment in comments:
            pprint(comment.model_dump())


@job_posting_app.command("create")
def job_posting_create(
    company_id: int = typer.Option(..., prompt=True),
    description: str = typer.Option(..., prompt=True),
    requirements: str = typer.Option("{}", prompt=True),
    keywords: str = typer.Option("{}", prompt=True),
) -> None:
    """Create a new job posting."""
    # Verify company exists
    company = db_manager.companies.get_by_id(company_id)
    if company is None:
        typer.echo(f"No company found with ID {company_id}.")
        raise typer.Exit(code=1)

    job_posting = JobPosting(
        company_id=company_id,
        description=description,
        requirements=requirements,
        keywords=keywords,
    )

    created_job_posting = db_manager.job_postings.create(job_posting)
    typer.echo(f"Job posting created with ID: {created_job_posting.id}")


@job_posting_app.command("update")
def job_posting_update(
    job_posting_id: int = typer.Option(..., "--job-posting-id"),
    description: str = typer.Option(None),
    requirements: str = typer.Option(None),
    keywords: str = typer.Option(None),
) -> None:
    """Update an existing job posting."""
    job_posting = db_manager.job_postings.get_by_id(job_posting_id)

    if job_posting is None:
        typer.echo(f"No job posting found with ID {job_posting_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if description is not None:
        job_posting.description = description
    if requirements is not None:
        job_posting.requirements = requirements
    if keywords is not None:
        job_posting.keywords = keywords

    job_posting.updated_at = datetime.datetime.now()
    db_manager.job_postings.update(job_posting)
    typer.echo(f"Job posting {job_posting_id} updated successfully.")


@job_posting_app.command("delete")
def job_posting_delete(job_posting_id: int) -> None:
    """Delete a job posting."""
    job_posting = db_manager.job_postings.get_by_id(job_posting_id)

    if job_posting is None:
        typer.echo(f"No job posting found with ID {job_posting_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(f"Delete job posting {job_posting_id}?"):
        db_manager.job_postings.delete(job_posting_id)
        typer.echo(f"Job posting {job_posting_id} deleted successfully.")


# ---------------------------------------------------------------------------
# Comment commands
# ---------------------------------------------------------------------------


@comment_app.command("list")
def comment_list(
    job_posting_id: int | None = typer.Option(None, "--job-posting-id"),
    company_id: int | None = typer.Option(None, "--company-id"),
) -> None:
    """List comments."""
    if job_posting_id:
        comments = db_manager.comments.get_by_job_posting_id(job_posting_id)
    elif company_id:
        comments = db_manager.comments.get_by_company_id(company_id)
    else:
        comments = db_manager.comments.get_all()

    if not comments:
        typer.echo("No comments found.")
        return

    table = Table(title="Comments")
    table.add_column("ID", style="cyan")
    table.add_column("Text", style="magenta")
    table.add_column("Job Posting ID", style="green")
    table.add_column("Company ID", style="yellow")
    table.add_column("Created", style="blue")

    for comment in comments:
        table.add_row(
            str(comment.id),
            comment.text[:50] + "..." if len(comment.text) > 50 else comment.text,
            str(comment.job_posting_id) if comment.job_posting_id else "-",
            str(comment.company_id) if comment.company_id else "-",
            comment.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@comment_app.command("show")
def comment_show(comment_id: int) -> None:
    """Show detailed information for a specific comment."""
    comment = db_manager.comments.get_by_id(comment_id)

    if comment is None:
        typer.echo(f"No comment found with ID {comment_id}.")
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]Comment Details[/bold cyan]")
    pprint(comment.model_dump())


@comment_app.command("create")
def comment_create(
    text: str = typer.Option(..., prompt=True),
    job_posting_id: int = typer.Option(None, prompt=True),
    company_id: int = typer.Option(None, prompt=True),
) -> None:
    """Create a new comment."""
    # Verify at least one reference is provided
    if job_posting_id is None and company_id is None:
        typer.echo("Either job_posting_id or company_id must be provided.")
        raise typer.Exit(code=1)

    # Verify job posting exists if provided
    if job_posting_id:
        job_posting = db_manager.job_postings.get_by_id(job_posting_id)
        if job_posting is None:
            typer.echo(f"No job posting found with ID {job_posting_id}.")
            raise typer.Exit(code=1)

    # Verify company exists if provided
    if company_id:
        company = db_manager.companies.get_by_id(company_id)
        if company is None:
            typer.echo(f"No company found with ID {company_id}.")
            raise typer.Exit(code=1)

    comment = Comment(
        text=text,
        job_posting_id=job_posting_id,
        company_id=company_id,
    )

    created_comment = db_manager.comments.create(comment)
    typer.echo(f"Comment created with ID: {created_comment.id}")


@comment_app.command("update")
def comment_update(
    comment_id: int = typer.Option(..., "--comment-id"),
    text: str = typer.Option(None),
) -> None:
    """Update an existing comment."""
    comment = db_manager.comments.get_by_id(comment_id)

    if comment is None:
        typer.echo(f"No comment found with ID {comment_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if text is not None:
        comment.text = text

    comment.updated_at = datetime.datetime.now()
    db_manager.comments.update(comment)
    typer.echo(f"Comment {comment_id} updated successfully.")


@comment_app.command("delete")
def comment_delete(comment_id: int) -> None:
    """Delete a comment."""
    comment = db_manager.comments.get_by_id(comment_id)

    if comment is None:
        typer.echo(f"No comment found with ID {comment_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(f"Delete comment '{comment.text[:30]}...'?"):
        db_manager.comments.delete(comment_id)
        typer.echo(f"Comment {comment_id} deleted successfully.")


# ---------------------------------------------------------------------------
# Candidate Response commands
# ---------------------------------------------------------------------------


@candidate_response_app.command("list")
def candidate_response_list(user_id: int | None = typer.Option(None, "--user-id")) -> None:
    """List candidate responses."""
    if user_id:
        responses = db_manager.candidate_responses.get_by_user_id(user_id)
    else:
        responses = db_manager.candidate_responses.get_all()

    if not responses:
        typer.echo("No candidate responses found.")
        return

    table = Table(title="Candidate Responses")
    table.add_column("ID", style="cyan")
    table.add_column("User ID", style="magenta")
    table.add_column("Prompt", style="green")
    table.add_column("Response", style="yellow")
    table.add_column("Created", style="blue")

    for response in responses:
        table.add_row(
            str(response.id),
            str(response.user_id),
            response.prompt[:50] + "..." if len(response.prompt) > 50 else response.prompt,
            response.response[:50] + "..." if len(response.response) > 50 else response.response,
            response.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)


@candidate_response_app.command("show")
def candidate_response_show(response_id: int) -> None:
    """Show detailed information for a specific candidate response."""
    response = db_manager.candidate_responses.get_by_id(response_id)

    if response is None:
        typer.echo(f"No candidate response found with ID {response_id}.")
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]Candidate Response Details[/bold cyan]")
    pprint(response.model_dump())


@candidate_response_app.command("create")
def candidate_response_create(
    user_id: int = typer.Option(..., prompt=True),
    prompt: str = typer.Option(..., prompt=True),
    response: str = typer.Option(..., prompt=True),
) -> None:
    """Create a new candidate response."""
    # Verify user exists
    user = db_manager.users.get_by_id(user_id)
    if user is None:
        typer.echo(f"No user found with ID {user_id}.")
        raise typer.Exit(code=1)

    candidate_response = CandidateResponse(
        user_id=user_id,
        prompt=prompt,
        response=response,
    )

    created_response = db_manager.candidate_responses.create(candidate_response)
    typer.echo(f"Candidate response created with ID: {created_response.id}")


@candidate_response_app.command("update")
def candidate_response_update(
    response_id: int = typer.Option(..., "--response-id"),
    prompt: str = typer.Option(None),
    response: str = typer.Option(None),
) -> None:
    """Update an existing candidate response."""
    candidate_response = db_manager.candidate_responses.get_by_id(response_id)

    if candidate_response is None:
        typer.echo(f"No candidate response found with ID {response_id}.")
        raise typer.Exit(code=1)

    # Update only provided fields
    if prompt is not None:
        candidate_response.prompt = prompt
    if response is not None:
        candidate_response.response = response

    candidate_response.updated_at = datetime.datetime.now()
    db_manager.candidate_responses.update(candidate_response)
    typer.echo(f"Candidate response {response_id} updated successfully.")


@candidate_response_app.command("delete")
def candidate_response_delete(response_id: int) -> None:
    """Delete a candidate response."""
    candidate_response = db_manager.candidate_responses.get_by_id(response_id)

    if candidate_response is None:
        typer.echo(f"No candidate response found with ID {response_id}.")
        raise typer.Exit(code=1)

    if typer.confirm(f"Delete candidate response '{candidate_response.prompt[:30]}...'?"):
        db_manager.candidate_responses.delete(response_id)
        typer.echo(f"Candidate response {response_id} deleted successfully.")
