"""Tests for alt text generation."""

import pytest
from unittest.mock import Mock, patch, MagicMock

try:
    from pdf_converter.alt_text_generator import AltTextGenerator, AltTextResult
    from pdf_converter.image_extractor import ExtractedImage
    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False


@pytest.mark.skipif(not HAS_MODULES, reason="Required modules not installed")
class TestAltTextResult:
    """Tests for AltTextResult dataclass."""

    def test_create_result(self):
        """Test creating an AltTextResult."""
        result = AltTextResult(
            alt_text="A bar chart showing quarterly sales",
            long_description="This bar chart displays quarterly sales data from Q1 to Q4 2024.",
            source="claude",
            success=True
        )

        assert result.alt_text == "A bar chart showing quarterly sales"
        assert result.source == "claude"
        assert result.success is True

    def test_default_success(self):
        """Test default success value."""
        result = AltTextResult(
            alt_text="test",
            long_description="test desc",
            source="ocr"
        )

        assert result.success is True


@pytest.mark.skipif(not HAS_MODULES, reason="Required modules not installed")
class TestAltTextGenerator:
    """Tests for AltTextGenerator class."""

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            gen = AltTextGenerator(api_key=None, use_ai=False)
            assert gen.use_ai is False

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        gen = AltTextGenerator(api_key='test-key', use_ai=True)
        # Even with a key, if anthropic fails to import, use_ai will be False
        # Just check the key was set
        assert gen.api_key == 'test-key'

    def test_generic_fallback(self):
        """Test generic fallback generation."""
        gen = AltTextGenerator(use_ai=False, use_ocr_fallback=False)

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=3,
            width=640,
            height=480
        )

        result = gen._generic_fallback(img)

        assert result.success is True
        assert result.source == 'generic'
        assert 'page 3' in result.alt_text.lower()
        assert '640x480' in result.long_description

    def test_caption_fallback(self):
        """Test caption-based fallback."""
        gen = AltTextGenerator(use_ai=False, use_ocr_fallback=False)

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=1,
            width=100,
            height=100,
            nearby_caption="Figure 1: Distribution of survey responses"
        )

        result = gen._use_caption_fallback(img)

        assert result.success is True
        assert result.source == 'caption'
        assert 'Distribution' in result.alt_text

    def test_caption_truncation(self):
        """Test that long captions are truncated."""
        gen = AltTextGenerator(use_ai=False, use_ocr_fallback=False)

        long_caption = "A" * 200  # Very long caption

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=1,
            width=100,
            height=100,
            nearby_caption=long_caption
        )

        result = gen._use_caption_fallback(img)

        assert len(result.alt_text) <= 150
        assert result.alt_text.endswith('...')

    def test_generate_with_caption(self):
        """Test generate uses caption when AI unavailable."""
        gen = AltTextGenerator(use_ai=False, use_ocr_fallback=False)

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=1,
            width=100,
            height=100,
            nearby_caption="Figure 1: Test image"
        )

        result = gen.generate(img)

        assert result.success is True
        assert result.source == 'caption'

    def test_generate_fallback_chain(self):
        """Test fallback chain when all options fail."""
        gen = AltTextGenerator(use_ai=False, use_ocr_fallback=False)

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=5,
            width=200,
            height=150
        )

        result = gen.generate(img)

        # Should fall back to generic
        assert result.success is True
        assert result.source == 'generic'

    @patch('pdf_converter.alt_text_generator.anthropic')
    def test_claude_api_call_format(self, mock_anthropic):
        """Test Claude API is called with correct format."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="ALT: Test description\nLONG: Extended description")]
        mock_client.messages.create.return_value = mock_response

        mock_anthropic.Anthropic.return_value = mock_client

        gen = AltTextGenerator(api_key='test-key', use_ai=True)
        gen._client = mock_client

        img = ExtractedImage(
            data=b'test_image_data',
            format='png',
            page=1,
            width=100,
            height=100,
            data_uri='data:image/png;base64,dGVzdA=='
        )

        result = gen._call_claude_vision(img, "Document context")

        # Verify API was called
        mock_client.messages.create.assert_called_once()

        # Check the call included an image
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs.get('messages', call_args.args[0] if call_args.args else [])
        assert len(messages) > 0

    def test_parse_response_standard_format(self):
        """Test parsing standard ALT/LONG format."""
        gen = AltTextGenerator(use_ai=False)

        response = "ALT: A simple test image\nLONG: This is a detailed description of the test image."
        alt, long_desc = gen._parse_response(response)

        assert alt == "A simple test image"
        assert "detailed description" in long_desc

    def test_parse_response_fallback(self):
        """Test parsing when format is non-standard."""
        gen = AltTextGenerator(use_ai=False)

        response = "This is just a plain description without the expected format."
        alt, long_desc = gen._parse_response(response)

        # Should still extract something useful
        assert alt != ""
        assert long_desc == response

    def test_build_prompt_with_context(self):
        """Test prompt building includes context."""
        gen = AltTextGenerator(use_ai=False)

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=1,
            width=100,
            height=100,
            nearby_caption="Figure 1: Test"
        )

        prompt = gen._build_prompt(img, "This is document context")

        assert "document context" in prompt.lower()
        assert "Figure 1: Test" in prompt

    def test_generate_batch(self):
        """Test batch generation."""
        gen = AltTextGenerator(use_ai=False, use_ocr_fallback=False)

        images = [
            ExtractedImage(
                data=b'test1',
                format='png',
                page=1,
                width=100,
                height=100,
                nearby_caption=f"Figure {i}: Caption"
            )
            for i in range(3)
        ]

        results = gen.generate_batch(images, context="Test doc", batch_delay=0)

        assert len(results) == 3
        assert all(r.success for r in results)


class TestRetryLogic:
    """Tests for retry and error handling."""

    @pytest.mark.skipif(not HAS_MODULES, reason="Required modules not installed")
    def test_max_retries(self):
        """Test that retries are limited."""
        gen = AltTextGenerator(use_ai=True, api_key='test')
        assert gen.MAX_RETRIES == 3

    @pytest.mark.skipif(not HAS_MODULES, reason="Required modules not installed")
    def test_base_delay(self):
        """Test base delay value."""
        gen = AltTextGenerator(use_ai=False)
        assert gen.BASE_DELAY == 1.0
