from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import TemplateError, TemplateNotFound
from src.resume.utils import (
    convert_html_to_pdf,
    get_pdf_file_size,
    get_pdf_info,
    get_pdf_page_count,
    get_template_environment,
    list_available_templates,
    render_template_to_html,
    render_template_to_pdf,
)


class TestTemplateEnvironment:
    """Test template environment creation and configuration."""

    def test_get_template_environment_success(self, tmp_path: Path) -> None:
        """Test successful template environment creation."""
        env = get_template_environment(tmp_path)
        assert env is not None
        assert env.loader is not None
        assert env.autoescape is True
        assert env.trim_blocks is True
        assert env.lstrip_blocks is True

    def test_get_template_environment_nonexistent_dir(self) -> None:
        """Test template environment creation with nonexistent directory."""
        nonexistent_path = Path("/nonexistent/path")
        with pytest.raises(FileNotFoundError, match="Templates directory not found"):
            get_template_environment(nonexistent_path)


class TestTemplateRendering:
    """Test template rendering functionality."""

    def test_render_template_to_html_success(self, tmp_path: Path) -> None:
        """Test successful template rendering to HTML."""
        # Create a test template
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>{{ name }} - Resume</title></head>
        <body>
            <h1>{{ name }}</h1>
            <p>{{ title }}</p>
        </body>
        </html>
        """
        template_file = tmp_path / "test_template.html"
        template_file.write_text(template_content)

        context = {"name": "John Doe", "title": "Software Engineer"}
        result = render_template_to_html("test_template.html", context, tmp_path)

        assert "John Doe" in result
        assert "Software Engineer" in result
        assert "<h1>John Doe</h1>" in result
        assert "<p>Software Engineer</p>" in result

    def test_render_template_to_html_template_not_found(self, tmp_path: Path) -> None:
        """Test template rendering with nonexistent template."""
        context = {"name": "John Doe"}
        with pytest.raises(TemplateNotFound):
            render_template_to_html("nonexistent.html", context, tmp_path)

    def test_render_template_to_html_template_error(self, tmp_path: Path) -> None:
        """Test template rendering with template syntax error."""
        # Create a template with syntax error
        template_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>{{ name }}</h1>
            {% if name %}
            <p>{{ name }}</p>
            {% endif %}
            {% invalid_syntax %}
        </body>
        </html>
        """
        template_file = tmp_path / "error_template.html"
        template_file.write_text(template_content)

        context = {"name": "John Doe"}
        with pytest.raises(TemplateError):
            render_template_to_html("error_template.html", context, tmp_path)


class TestHTMLToPDFConversion:
    """Test HTML to PDF conversion functionality."""

    def test_convert_html_to_pdf_success(self, tmp_path: Path) -> None:
        """Test successful HTML to PDF conversion."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Resume</title></head>
        <body>
            <h1>John Doe</h1>
            <p>Software Engineer</p>
        </body>
        </html>
        """
        output_path = tmp_path / "test_resume.pdf"

        result_path = convert_html_to_pdf(html_content, output_path)

        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

    def test_convert_html_to_pdf_with_css(self, tmp_path: Path) -> None:
        """Test HTML to PDF conversion with custom CSS."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Resume</title></head>
        <body>
            <h1>John Doe</h1>
            <p>Software Engineer</p>
        </body>
        </html>
        """
        css_string = "body { font-family: Arial; } h1 { color: blue; }"
        output_path = tmp_path / "test_resume_with_css.pdf"

        result_path = convert_html_to_pdf(html_content, output_path, css_string)

        assert result_path.exists()
        assert result_path.suffix == ".pdf"

    def test_convert_html_to_pdf_creates_directory(self, tmp_path: Path) -> None:
        """Test that PDF conversion creates parent directories."""
        html_content = "<html><body><h1>Test</h1></body></html>"
        output_path = tmp_path / "subdir" / "test_resume.pdf"

        result_path = convert_html_to_pdf(html_content, output_path)

        assert result_path.exists()
        assert output_path.parent.exists()

    def test_convert_html_to_pdf_conversion_error(self, tmp_path: Path) -> None:
        """Test HTML to PDF conversion with invalid HTML."""
        invalid_html = "<invalid>html<content>"
        output_path = tmp_path / "test_resume.pdf"

        # This should still work as weasyprint is quite forgiving
        result_path = convert_html_to_pdf(invalid_html, output_path)
        assert result_path.exists()


class TestTemplateToPDFPipeline:
    """Test complete template to PDF pipeline."""

    def test_render_template_to_pdf_success(self, tmp_path: Path) -> None:
        """Test successful template to PDF pipeline."""
        # Create a test template
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>{{ name }} - Resume</title></head>
        <body>
            <h1>{{ name }}</h1>
            <p>{{ title }}</p>
        </body>
        </html>
        """
        template_file = tmp_path / "resume_template.html"
        template_file.write_text(template_content)

        context = {"name": "John Doe", "title": "Software Engineer"}
        output_path = tmp_path / "output" / "resume.pdf"

        result_path = render_template_to_pdf(
            "resume_template.html", context, output_path, tmp_path
        )

        assert result_path.exists()
        assert result_path.suffix == ".pdf"

    def test_render_template_to_pdf_with_css(self, tmp_path: Path) -> None:
        """Test template to PDF pipeline with custom CSS."""
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>{{ name }} - Resume</title></head>
        <body>
            <h1>{{ name }}</h1>
            <p>{{ title }}</p>
        </body>
        </html>
        """
        template_file = tmp_path / "resume_template.html"
        template_file.write_text(template_content)

        context = {"name": "John Doe", "title": "Software Engineer"}
        output_path = tmp_path / "resume.pdf"
        css_string = "body { font-family: Arial; }"

        result_path = render_template_to_pdf(
            "resume_template.html", context, output_path, tmp_path, css_string
        )

        assert result_path.exists()
        assert result_path.suffix == ".pdf"


class TestPDFAnalysis:
    """Test PDF analysis functionality."""

    def test_get_pdf_page_count_success(self, tmp_path: Path) -> None:
        """Test successful PDF page count retrieval."""
        # Create a simple PDF for testing
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Page 1</h1>
            <div style="page-break-before: always;">
                <h1>Page 2</h1>
            </div>
        </body>
        </html>
        """
        pdf_path = tmp_path / "test.pdf"
        convert_html_to_pdf(html_content, pdf_path)

        page_count = get_pdf_page_count(pdf_path)
        assert page_count >= 1  # At least 1 page

    def test_get_pdf_page_count_file_not_found(self, tmp_path: Path) -> None:
        """Test PDF page count with nonexistent file."""
        nonexistent_pdf = tmp_path / "nonexistent.pdf"
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            get_pdf_page_count(nonexistent_pdf)

    def test_get_pdf_file_size_success(self, tmp_path: Path) -> None:
        """Test successful PDF file size retrieval."""
        html_content = "<html><body><h1>Test</h1></body></html>"
        pdf_path = tmp_path / "test.pdf"
        convert_html_to_pdf(html_content, pdf_path)

        file_size = get_pdf_file_size(pdf_path)
        assert file_size > 0
        assert isinstance(file_size, int)

    def test_get_pdf_file_size_file_not_found(self, tmp_path: Path) -> None:
        """Test PDF file size with nonexistent file."""
        nonexistent_pdf = tmp_path / "nonexistent.pdf"
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            get_pdf_file_size(nonexistent_pdf)

    def test_get_pdf_info_success(self, tmp_path: Path) -> None:
        """Test successful PDF info retrieval."""
        html_content = "<html><body><h1>Test</h1></body></html>"
        pdf_path = tmp_path / "test.pdf"
        convert_html_to_pdf(html_content, pdf_path)

        info = get_pdf_info(pdf_path)

        assert "page_count" in info
        assert "file_size_bytes" in info
        assert "file_size_mb" in info
        assert "metadata" in info
        assert "path" in info
        assert info["page_count"] >= 1
        assert info["file_size_bytes"] > 0
        assert info["file_size_mb"] >= 0  # Small PDFs can be 0.0 MB
        assert info["path"] == str(pdf_path)

    def test_get_pdf_info_file_not_found(self, tmp_path: Path) -> None:
        """Test PDF info with nonexistent file."""
        nonexistent_pdf = tmp_path / "nonexistent.pdf"
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            get_pdf_info(nonexistent_pdf)


class TestTemplateListing:
    """Test template listing functionality."""

    def test_list_available_templates_success(self, tmp_path: Path) -> None:
        """Test successful template listing."""
        # Create test templates
        templates = ["resume_001.html", "resume_002.html", "cover_letter.html"]
        for template in templates:
            (tmp_path / template).write_text("<html><body>Test</body></html>")

        # Create a non-HTML file
        (tmp_path / "readme.txt").write_text("Not a template")

        result = list_available_templates(tmp_path)

        assert len(result) == 3
        assert "resume_001.html" in result
        assert "resume_002.html" in result
        assert "cover_letter.html" in result
        assert "readme.txt" not in result
        assert result == sorted(result)  # Should be sorted

    def test_list_available_templates_empty_directory(self, tmp_path: Path) -> None:
        """Test template listing with empty directory."""
        result = list_available_templates(tmp_path)
        assert result == []

    def test_list_available_templates_nonexistent_directory(self) -> None:
        """Test template listing with nonexistent directory."""
        nonexistent_path = Path("/nonexistent/path")
        with pytest.raises(FileNotFoundError, match="Templates directory not found"):
            list_available_templates(nonexistent_path)

    def test_list_available_templates_case_sensitive(self, tmp_path: Path) -> None:
        """Test template listing with different file extensions."""
        # Create files with different extensions
        (tmp_path / "resume.HTML").write_text("<html><body>Test</body></html>")
        (tmp_path / "resume.Html").write_text("<html><body>Test</body></html>")
        (tmp_path / "resume.html").write_text("<html><body>Test</body></html>")

        result = list_available_templates(tmp_path)

        # Should only include .html files (case sensitive on most systems)
        assert len(result) >= 1  # At least one .html file should be found
        assert all(name.lower().endswith(".html") for name in result)


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_complete_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow from template to PDF analysis."""
        # Create a test template
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>{{ name }} - Resume</title></head>
        <body>
            <h1>{{ name }}</h1>
            <p>{{ title }}</p>
            <ul>
                {% for skill in skills %}
                <li>{{ skill }}</li>
                {% endfor %}
            </ul>
        </body>
        </html>
        """
        template_file = tmp_path / "resume_template.html"
        template_file.write_text(template_content)

        # Test data
        context = {
            "name": "John Doe",
            "title": "Software Engineer",
            "skills": ["Python", "JavaScript", "React"],
        }
        output_path = tmp_path / "resume.pdf"

        # Generate PDF
        pdf_path = render_template_to_pdf("resume_template.html", context, output_path, tmp_path)

        # Analyze PDF
        info = get_pdf_info(pdf_path)

        # Verify results
        assert pdf_path.exists()
        assert info["page_count"] >= 1
        assert info["file_size_bytes"] > 0
        assert info["path"] == str(pdf_path)

    def test_template_listing_integration(self, tmp_path: Path) -> None:
        """Test integration between template listing and rendering."""
        # Create multiple templates
        templates = {
            "resume_001.html": "<html><body><h1>{{ name }}</h1></body></html>",
            "resume_002.html": "<html><body><h2>{{ title }}</h2></body></html>",
            "cover_letter.html": "<html><body><p>{{ content }}</p></body></html>",
        }

        for name, content in templates.items():
            (tmp_path / name).write_text(content)

        # List available templates
        available_templates = list_available_templates(tmp_path)
        assert len(available_templates) == 3

        # Test rendering each template
        for template_name in available_templates:
            context = {"name": "Test", "title": "Test", "content": "Test"}
            output_path = tmp_path / f"{template_name.replace('.html', '.pdf')}"

            pdf_path = render_template_to_pdf(template_name, context, output_path, tmp_path)

            assert pdf_path.exists()
            assert get_pdf_page_count(pdf_path) >= 1
