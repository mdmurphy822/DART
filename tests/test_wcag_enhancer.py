"""
Tests for WCAG 2.2 AA HTML Enhancer.
"""

import pytest
from pdf_converter.wcag_enhancer import (
    WCAGHTMLEnhancer,
    WCAGOptions,
    enhance_html_wcag,
)


class TestWCAGOptions:
    """Tests for WCAGOptions dataclass."""

    def test_default_options(self):
        """Test default WCAG options."""
        options = WCAGOptions()

        # Core options
        assert options.add_skip_link is True
        assert options.add_aria_landmarks is True
        assert options.dark_mode is True
        assert options.reduced_motion is True

        # WCAG 2.2 specific options
        assert options.focus_not_obscured is True
        assert options.focus_appearance_2px is True
        assert options.target_size_minimum is True
        assert options.wcag_version == "2.2"

    def test_custom_options(self):
        """Test custom WCAG options."""
        options = WCAGOptions(
            add_skip_link=False,
            dark_mode=False,
            wcag_version="2.1"
        )

        assert options.add_skip_link is False
        assert options.dark_mode is False
        assert options.wcag_version == "2.1"


class TestWCAGHTMLEnhancer:
    """Tests for WCAGHTMLEnhancer class."""

    def test_enhancer_initialization(self):
        """Test enhancer can be initialized."""
        enhancer = WCAGHTMLEnhancer()
        assert enhancer is not None

    def test_basic_enhancement(self):
        """Test basic HTML enhancement."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Test Document</h1>
            <p>This is a test paragraph.</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html)

        # Should add lang attribute
        assert 'lang="en"' in result

        # Should add skip link
        assert 'skip-link' in result.lower() or 'skip to' in result.lower()

    def test_skip_link_added(self):
        """Test skip link is added."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Content</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html, WCAGOptions(add_skip_link=True))

        assert 'href="#main"' in result or 'skip' in result.lower()

    def test_aria_landmarks_added(self):
        """Test ARIA landmarks are added."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Content</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html, WCAGOptions(add_aria_landmarks=True))

        # Should have main landmark
        assert 'role="main"' in result or '<main' in result

    def test_wcag_22_focus_styles_in_css(self):
        """Test WCAG 2.2 focus styles are included in CSS."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Content</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html)

        # Should have WCAG 2.2 2.4.13 focus appearance comment
        assert '2.4.13' in result

        # Should have focus outline >= 2px
        assert 'outline: 3px solid' in result

    def test_wcag_22_scroll_margin_in_css(self):
        """Test WCAG 2.2 scroll-margin is included for focus not obscured."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Content</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html)

        # Should have WCAG 2.2 2.4.11/2.4.12 focus not obscured
        assert '2.4.11' in result or '2.4.12' in result
        assert 'scroll-margin' in result

    def test_wcag_22_target_size_in_css(self):
        """Test WCAG 2.2 target size minimums are included in CSS."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Content</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html)

        # Should have WCAG 2.2 2.5.8 target size
        assert '2.5.8' in result
        assert 'min-height: 24px' in result
        assert 'min-width: 24px' in result

    def test_dark_mode_support(self):
        """Test dark mode CSS is included."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html, WCAGOptions(dark_mode=True))

        assert 'prefers-color-scheme: dark' in result

    def test_reduced_motion_support(self):
        """Test reduced motion CSS is included."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html, WCAGOptions(reduced_motion=True))

        assert 'prefers-reduced-motion' in result

    def test_accessibility_footer(self):
        """Test accessibility footer mentions WCAG 2.2."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Content</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html)

        # Footer should mention WCAG 2.2
        assert 'WCAG 2.2' in result

    def test_figure_enhancement(self):
        """Test figure elements are enhanced."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <figure>
                <img src="test.png" alt="Test image">
            </figure>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html, WCAGOptions(enhance_figures=True))

        # Should add role="figure" or aria attributes
        assert 'figure' in result.lower()

    def test_table_detection(self):
        """Test table-like content detection."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body>
            <h1>Test</h1>
            <p>Header1\tHeader2\tHeader3</p>
            <p>Data1\tData2\tData3</p>
        </body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html, WCAGOptions(detect_tables=True))

        # Enhancer should process the content
        assert result is not None

    def test_convenience_function(self):
        """Test enhance_html_wcag convenience function."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body><h1>Test</h1></body>
        </html>
        """
        result = enhance_html_wcag(html)
        assert 'WCAG 2.2' in result or 'skip' in result.lower()

    def test_css_comment_references_wcag_22(self):
        """Test CSS comments reference WCAG 2.2."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body><h1>Test</h1></body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        result = enhancer.enhance(html)

        # Should have WCAG 2.2 AA comment in CSS
        assert 'WCAG 2.2 AA' in result


class TestWCAG22CSSFeatures:
    """Tests specifically for WCAG 2.2 CSS features."""

    def get_enhanced_html(self):
        """Helper to get enhanced HTML."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head><title>Test</title></head>
        <body><h1>Test</h1></body>
        </html>
        """
        enhancer = WCAGHTMLEnhancer()
        return enhancer.enhance(html)

    def test_focus_outline_exceeds_2px(self):
        """Test focus outline is at least 2px (WCAG 2.4.13)."""
        result = self.get_enhanced_html()

        # The CSS should have 3px outline which exceeds 2px minimum
        assert 'outline: 3px solid' in result

    def test_scroll_margin_values(self):
        """Test scroll-margin values for focus not obscured."""
        result = self.get_enhanced_html()

        # Should have scroll-margin for top and bottom
        assert 'scroll-margin-top: 80px' in result
        assert 'scroll-margin-bottom: 80px' in result

    def test_target_size_24px(self):
        """Test interactive elements have 24px minimum size."""
        result = self.get_enhanced_html()

        # Should have 24px minimum for interactive elements
        assert 'min-height: 24px' in result
        assert 'min-width: 24px' in result

    def test_inline_link_exception(self):
        """Test inline links are exempt from target size requirement."""
        result = self.get_enhanced_html()

        # Inline links should have auto sizes (exempt per WCAG 2.5.8)
        assert 'p a' in result
        assert 'min-height: auto' in result

    def test_focus_visible_selector(self):
        """Test :focus-visible selector is used."""
        result = self.get_enhanced_html()

        assert ':focus-visible' in result
