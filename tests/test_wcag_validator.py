"""
Tests for WCAG 2.2 AA Validator.
"""

import pytest
from pdf_converter.wcag_validator import (
    WCAGValidator,
    ValidationReport,
    WCAGIssue,
    IssueSeverity,
    WCAGCriterion,
    validate_html_wcag,
)


class TestWCAGValidator:
    """Tests for WCAGValidator class."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = WCAGValidator()
        assert validator is not None
        assert not validator.strict_mode

        strict_validator = WCAGValidator(strict_mode=True)
        assert strict_validator.strict_mode

    def test_valid_html_passes(self):
        """Test that valid accessible HTML passes validation."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Test Document</title>
            <style>
                :focus { outline: 3px solid #0066cc; outline-offset: 2px; }
                *:focus { scroll-margin-top: 80px; scroll-margin-bottom: 80px; }
            </style>
        </head>
        <body>
            <a href="#main" class="skip-link">Skip to main content</a>
            <header role="banner">
                <h1>Test Document</h1>
            </header>
            <main id="main" role="main">
                <h2>Introduction</h2>
                <p>This is a test paragraph with proper structure.</p>
                <img src="test.png" alt="A descriptive alt text for this test image">
            </main>
            <footer role="contentinfo">
                <p>Footer content</p>
            </footer>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        assert report.critical_count == 0
        assert report.wcag_aa_compliant

    def test_missing_language_declaration(self):
        """Test detection of missing lang attribute."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body><main><h1>Test</h1></main></body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        # Should have critical issue for missing lang
        lang_issues = [i for i in report.issues if i.criterion == "3.1.1"]
        assert len(lang_issues) > 0
        assert any(i.severity == IssueSeverity.CRITICAL for i in lang_issues)

    def test_missing_page_title(self):
        """Test detection of missing page title."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head></head>
        <body><main><h1>Test</h1></main></body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        title_issues = [i for i in report.issues if i.criterion == "2.4.2"]
        assert len(title_issues) > 0

    def test_missing_alt_text(self):
        """Test detection of missing alt text on images."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Test</h1>
                <img src="test.png">
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        alt_issues = [i for i in report.issues if i.criterion == "1.1.1"]
        assert len(alt_issues) > 0
        assert any(i.severity == IssueSeverity.CRITICAL for i in alt_issues)

    def test_generic_alt_text(self):
        """Test detection of generic alt text."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Test</h1>
                <img src="test.png" alt="image">
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        alt_issues = [i for i in report.issues if i.criterion == "1.1.1"]
        assert len(alt_issues) > 0
        assert any("generic" in i.message.lower() for i in alt_issues)

    def test_heading_hierarchy(self):
        """Test detection of skipped heading levels."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Title</h1>
                <h4>Skipped from h1 to h4</h4>
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        heading_issues = [i for i in report.issues if i.criterion == "1.3.1" and "skipped" in i.message.lower()]
        assert len(heading_issues) > 0

    def test_no_h1(self):
        """Test detection of missing h1 element."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h2>Section</h2>
                <p>Content</p>
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        h1_issues = [i for i in report.issues if "h1" in i.message.lower()]
        assert len(h1_issues) > 0

    def test_generic_link_text(self):
        """Test detection of generic link text."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Test</h1>
                <p><a href="page.html">click here</a></p>
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        link_issues = [i for i in report.issues if i.criterion == "2.4.4"]
        assert len(link_issues) > 0

    def test_form_without_labels(self):
        """Test detection of form inputs without labels."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Test Form</h1>
                <form>
                    <input type="text" name="username">
                </form>
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        form_issues = [i for i in report.issues if "form" in i.message.lower() or "label" in i.message.lower()]
        assert len(form_issues) > 0

    def test_table_without_headers(self):
        """Test detection of tables without header cells."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Test</h1>
                <table>
                    <tr><td>Data 1</td><td>Data 2</td></tr>
                </table>
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        table_issues = [i for i in report.issues if "table" in i.message.lower() and "header" in i.message.lower()]
        assert len(table_issues) > 0

    def test_focus_outline_removal(self):
        """Test detection of focus outline removal."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Test</title>
            <style>
                :focus { outline: none; }
            </style>
        </head>
        <body>
            <main><h1>Test</h1></main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        focus_issues = [i for i in report.issues if i.criterion == "2.4.7"]
        assert len(focus_issues) > 0

    def test_wcag_22_focus_appearance(self):
        """Test WCAG 2.2 focus appearance validation (2.4.13)."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Test</title>
            <style>
                :focus { outline: 1px solid black; }
            </style>
        </head>
        <body>
            <main><h1>Test</h1></main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        focus_appearance_issues = [i for i in report.issues if i.criterion == "2.4.13"]
        assert len(focus_appearance_issues) > 0
        assert any("1px" in i.message for i in focus_appearance_issues)

    def test_wcag_22_focus_not_obscured(self):
        """Test WCAG 2.2 focus not obscured validation (2.4.11/2.4.12)."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Test</title>
            <style>
                .header { position: fixed; top: 0; }
            </style>
        </head>
        <body>
            <header class="header">Fixed Header</header>
            <main><h1>Test</h1></main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        # Should warn about fixed elements without scroll-margin
        focus_obscured_issues = [i for i in report.issues if i.criterion == "2.4.11"]
        assert len(focus_obscured_issues) > 0

    def test_wcag_22_target_size(self):
        """Test WCAG 2.2 target size validation (2.5.8)."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Test</title>
            <style>
                button { width: 16px; height: 16px; }
            </style>
        </head>
        <body>
            <main>
                <h1>Test</h1>
                <button>X</button>
            </main>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        target_size_issues = [i for i in report.issues if i.criterion == "2.5.8"]
        assert len(target_size_issues) > 0

    def test_report_to_json(self):
        """Test JSON report generation."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body><main><h1>Test</h1></main></body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        json_output = report.to_json()
        assert "file_path" in json_output
        assert "wcag_aa_compliant" in json_output
        assert "issues" in json_output

    def test_report_to_text(self):
        """Test text report generation."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body><main><h1>Test</h1></main></body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        text_output = report.to_text()
        assert "WCAG 2.2 AA" in text_output
        assert "VALIDATION REPORT" in text_output

    def test_strict_mode(self):
        """Test strict mode treats high severity as non-compliant."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <main>
                <h1>Test</h1>
                <img src="test.png" alt="image">
            </main>
        </body>
        </html>
        """
        # Non-strict mode
        validator = WCAGValidator(strict_mode=False)
        report = validator.validate(html)

        # Strict mode should be more restrictive
        strict_validator = WCAGValidator(strict_mode=True)
        strict_report = strict_validator.validate(html)

        # Both should have the same issues, but strict mode may fail compliance
        assert strict_report.high_count == report.high_count

    def test_convenience_function(self):
        """Test validate_html_wcag convenience function."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body><main><h1>Test</h1></main></body>
        </html>
        """
        report = validate_html_wcag(html)
        assert isinstance(report, ValidationReport)


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    def test_report_counts(self):
        """Test that report correctly counts issues by severity."""
        html = """
        <!DOCTYPE html>
        <html>
        <head></head>
        <body>
            <img src="test.png">
            <table><tr><td>Data</td></tr></table>
        </body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(html)

        # Should have multiple issues
        assert report.total_issues > 0
        assert report.total_issues == (
            report.critical_count + report.high_count +
            report.medium_count + report.low_count
        )

    def test_compliance_determination(self):
        """Test WCAG AA compliance determination."""
        # HTML with critical issues should not be compliant
        bad_html = """
        <!DOCTYPE html>
        <html>
        <head></head>
        <body><img src="test.png"></body>
        </html>
        """
        validator = WCAGValidator()
        report = validator.validate(bad_html)
        assert not report.wcag_aa_compliant
        assert report.critical_count > 0


class TestWCAGCriterion:
    """Tests for WCAG criterion enumeration."""

    def test_wcag_22_criteria_exist(self):
        """Test that WCAG 2.2 specific criteria are defined."""
        # WCAG 2.2 Level A
        assert WCAGCriterion.SC_2_4_11.value == "2.4.11"

        # WCAG 2.2 Level AA
        assert WCAGCriterion.SC_2_4_12.value == "2.4.12"
        assert WCAGCriterion.SC_2_4_13.value == "2.4.13"
        assert WCAGCriterion.SC_2_5_8.value == "2.5.8"


class TestIssueSeverity:
    """Tests for issue severity enumeration."""

    def test_severity_levels(self):
        """Test severity levels are properly defined."""
        assert IssueSeverity.CRITICAL.value == "critical"
        assert IssueSeverity.HIGH.value == "high"
        assert IssueSeverity.MEDIUM.value == "medium"
        assert IssueSeverity.LOW.value == "low"
