"""Tests for math detection and MathML conversion."""

import pytest
from pdf_converter.math_processor import MathDetector, MathMLConverter, MathBlock


class TestMathDetector:
    """Tests for MathDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = MathDetector()

    def test_detect_inline_latex(self):
        """Test detection of inline LaTeX ($...$)."""
        text = "The equation $x^2 + y^2 = z^2$ is the Pythagorean theorem."
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) == 1
        assert blocks[0].source_type == 'latex_inline'
        assert blocks[0].raw_content == 'x^2 + y^2 = z^2'

    def test_detect_display_latex(self):
        """Test detection of display LaTeX ($$...$$)."""
        text = "Consider the formula: $$\\frac{a}{b} = c$$"
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) == 1
        assert blocks[0].source_type == 'latex_display'
        assert '\\frac{a}{b}' in blocks[0].raw_content

    def test_avoid_currency_false_positive(self):
        """Test that currency amounts are not detected as math."""
        text = "The price is $50 and the total is $100.00"
        blocks = self.detector.detect_in_text(text)

        # Should not detect currency as math
        assert len(blocks) == 0

    def test_detect_latex_commands(self):
        """Test detection of LaTeX commands in text."""
        text = "The sum is $\\sum_{i=1}^{n} x_i$ over all values."
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) == 1
        assert '\\sum' in blocks[0].raw_content

    def test_detect_unicode_math(self):
        """Test detection of Unicode math symbols."""
        text = "We have the integral for all n."
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) >= 1

    def test_fallback_text_generation(self):
        """Test that fallback text is generated."""
        text = "The fraction $\\frac{a}{b}$ represents division."
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) == 1
        assert 'over' in blocks[0].fallback_text.lower()

    def test_empty_text(self):
        """Test with empty input."""
        blocks = self.detector.detect_in_text("")
        assert len(blocks) == 0

    def test_no_math(self):
        """Test text with no math."""
        text = "This is just regular text without any mathematical content."
        blocks = self.detector.detect_in_text(text)
        assert len(blocks) == 0

    def test_multiple_expressions(self):
        """Test text with multiple math expressions."""
        text = "Given $a + b$ and $c - d$, we find $a + b + c - d$."
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) == 3

    def test_latex_bracket_notation(self):
        """Test \\[...\\] notation."""
        text = "The formula is \\[E = mc^2\\] which is famous."
        blocks = self.detector.detect_in_text(text)

        assert len(blocks) == 1
        assert blocks[0].source_type == 'latex_display'


class TestMathMLConverter:
    """Tests for MathMLConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = MathMLConverter()

    def test_basic_conversion(self):
        """Test basic LaTeX to MathML conversion."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='x^2',
            mathml='',
            fallback_text='x squared'
        )

        self.converter.convert(block)

        assert block.mathml != ''
        assert '<math' in block.mathml
        assert 'xmlns' in block.mathml

    def test_fraction_conversion(self):
        """Test fraction conversion."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='\\frac{a}{b}',
            mathml='',
            fallback_text='a over b'
        )

        self.converter.convert(block)

        assert '<mfrac>' in block.mathml

    def test_superscript_conversion(self):
        """Test superscript conversion."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='x^2',
            mathml='',
            fallback_text='x squared'
        )

        self.converter.convert(block)

        assert '<msup>' in block.mathml

    def test_subscript_conversion(self):
        """Test subscript conversion."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='x_i',
            mathml='',
            fallback_text='x subscript i'
        )

        self.converter.convert(block)

        assert '<msub>' in block.mathml

    def test_sqrt_conversion(self):
        """Test square root conversion."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='\\sqrt{x}',
            mathml='',
            fallback_text='square root of x'
        )

        self.converter.convert(block)

        assert '<msqrt>' in block.mathml

    def test_greek_letter_conversion(self):
        """Test Greek letter conversion."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='\\alpha + \\beta',
            mathml='',
            fallback_text='alpha plus beta'
        )

        self.converter.convert(block)

        # Should have Greek letter entities
        assert '03B1' in block.mathml or 'alpha' in block.mathml.lower()

    def test_unicode_to_mathml(self):
        """Test Unicode math to MathML conversion."""
        mathml = self.converter.unicode_to_mathml('x + y')

        assert '<math' in mathml
        assert '<mo>+</mo>' in mathml

    def test_display_mode(self):
        """Test display mode attribute."""
        mathml = self.converter.latex_to_mathml('x^2', display=True)

        assert 'display="block"' in mathml

    def test_accessible_fallback(self):
        """Test accessible fallback generation."""
        fallback = self.converter.create_accessible_fallback('x^2', 'x squared')

        assert 'role="math"' in fallback
        assert 'aria-label="x squared"' in fallback


class TestMathBlockDataclass:
    """Tests for MathBlock dataclass."""

    def test_create_mathblock(self):
        """Test creating a MathBlock."""
        block = MathBlock(
            source_type='latex_inline',
            raw_content='x + y',
            mathml='<math>...</math>',
            fallback_text='x plus y',
            start_pos=10,
            end_pos=20
        )

        assert block.source_type == 'latex_inline'
        assert block.raw_content == 'x + y'
        assert block.start_pos == 10
        assert block.end_pos == 20

    def test_default_positions(self):
        """Test default position values."""
        block = MathBlock(
            source_type='unicode',
            raw_content='',
            mathml='',
            fallback_text=''
        )

        assert block.start_pos == 0
        assert block.end_pos == 0
