"""Tests for image extraction and processing."""

import pytest
import io
from unittest.mock import Mock, patch, MagicMock

# These tests can run without PyMuPDF installed
try:
    from pdf_converter.image_extractor import (
        PDFImageExtractor,
        ImageProcessor,
        ExtractedImage
    )
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


@pytest.mark.skipif(not HAS_PYMUPDF, reason="PyMuPDF not installed")
class TestExtractedImage:
    """Tests for ExtractedImage dataclass."""

    def test_create_extracted_image(self):
        """Test creating an ExtractedImage."""
        img = ExtractedImage(
            data=b'fake_image_data',
            format='png',
            page=1,
            width=800,
            height=600,
            bbox=(0, 0, 800, 600),
            nearby_caption='Figure 1: Test image',
            data_uri='data:image/png;base64,abc123',
            image_hash='abc123hash'
        )

        assert img.format == 'png'
        assert img.page == 1
        assert img.width == 800
        assert img.height == 600
        assert img.nearby_caption == 'Figure 1: Test image'

    def test_default_values(self):
        """Test default values."""
        img = ExtractedImage(
            data=b'data',
            format='jpeg',
            page=1,
            width=100,
            height=100
        )

        assert img.bbox == (0, 0, 0, 0)
        assert img.nearby_caption == ''
        assert img.data_uri == ''
        assert img.alt_text == ''


@pytest.mark.skipif(not HAS_PYMUPDF, reason="PyMuPDF not installed")
class TestPDFImageExtractor:
    """Tests for PDFImageExtractor class."""

    def test_init_with_missing_file(self):
        """Test initialization with non-existent file."""
        extractor = PDFImageExtractor('/nonexistent/path.pdf')
        # Should not raise, but _doc should be None
        assert extractor._doc is None

    def test_extract_all_empty_doc(self):
        """Test extracting from empty/missing document."""
        extractor = PDFImageExtractor('/nonexistent/path.pdf')
        images = extractor.extract_all()
        assert images == []

    @patch('pdf_converter.image_extractor.fitz')
    def test_extract_all_with_mock(self, mock_fitz):
        """Test extraction with mocked PyMuPDF."""
        # Set up mock document
        mock_doc = MagicMock()
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__iter__ = Mock(return_value=iter([MagicMock()]))

        mock_page = MagicMock()
        mock_page.get_images.return_value = []
        mock_doc.__getitem__ = Mock(return_value=mock_page)

        mock_fitz.open.return_value = mock_doc

        extractor = PDFImageExtractor('test.pdf')
        images = extractor.extract_all()

        assert isinstance(images, list)

    def test_get_mime_type(self):
        """Test MIME type detection."""
        extractor = PDFImageExtractor.__new__(PDFImageExtractor)
        extractor._doc = None
        extractor._fitz = None

        assert extractor._get_mime_type('png') == 'image/png'
        assert extractor._get_mime_type('jpg') == 'image/jpeg'
        assert extractor._get_mime_type('jpeg') == 'image/jpeg'
        assert extractor._get_mime_type('gif') == 'image/gif'
        assert extractor._get_mime_type('unknown') == 'image/png'

    def test_context_manager(self):
        """Test context manager usage."""
        with PDFImageExtractor('/nonexistent.pdf') as extractor:
            assert extractor is not None


class TestImageProcessor:
    """Tests for ImageProcessor class."""

    def test_init_defaults(self):
        """Test initialization with defaults."""
        try:
            from pdf_converter.image_extractor import ImageProcessor
            processor = ImageProcessor()
            assert processor.max_width == 800
            assert processor.quality == 85
        except ImportError:
            pytest.skip("ImageProcessor not available")

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        try:
            from pdf_converter.image_extractor import ImageProcessor
            processor = ImageProcessor(max_width=1200, quality=90)
            assert processor.max_width == 1200
            assert processor.quality == 90
        except ImportError:
            pytest.skip("ImageProcessor not available")

    @pytest.mark.skipif(not HAS_PYMUPDF, reason="PyMuPDF not installed")
    def test_process_without_pil(self):
        """Test processing when PIL is not available."""
        processor = ImageProcessor()
        processor._pil = None

        img = ExtractedImage(
            data=b'test',
            format='png',
            page=1,
            width=100,
            height=100
        )

        result = processor.process(img)
        # Should return unchanged image
        assert result.data == b'test'

    @patch('pdf_converter.image_extractor.Image')
    def test_process_with_mock_pil(self, mock_pil_module):
        """Test processing with mocked PIL."""
        try:
            from pdf_converter.image_extractor import ImageProcessor

            # Create a processor
            processor = ImageProcessor(max_width=400)

            # Create mock image
            mock_img = MagicMock()
            mock_img.width = 800
            mock_img.height = 600
            mock_img.mode = 'RGB'
            mock_img.size = (800, 600)

            # Mock resize
            resized = MagicMock()
            resized.width = 400
            resized.height = 300
            resized.mode = 'RGB'
            mock_img.resize.return_value = resized

            # Mock save
            def mock_save(output, **kwargs):
                output.write(b'compressed_data')

            resized.save = mock_save

            # Mock open
            mock_pil_module.Image.open.return_value = mock_img
            mock_pil_module.Image.LANCZOS = 1

            processor._pil = mock_pil_module

            img = ExtractedImage(
                data=b'original_data',
                format='png',
                page=1,
                width=800,
                height=600
            )

            result = processor.process(img)

            # Should have been processed
            assert result is not None

        except ImportError:
            pytest.skip("ImageProcessor not available")


class TestCaptionDetection:
    """Tests for caption pattern detection."""

    @pytest.mark.skipif(not HAS_PYMUPDF, reason="PyMuPDF not installed")
    def test_caption_patterns(self):
        """Test that caption patterns match correctly."""
        extractor = PDFImageExtractor.__new__(PDFImageExtractor)
        extractor._doc = None
        extractor._fitz = None

        patterns = extractor.CAPTION_PATTERNS

        # Test various caption formats
        test_cases = [
            "Figure 1: Test caption",
            "Fig. 2: Another caption",
            "Figure 10. Description here",
            "Image 3: Some image",
            "Chart 1: Data visualization",
        ]

        for caption in test_cases:
            matched = any(p.match(caption) for p in patterns)
            assert matched, f"Pattern should match: {caption}"

    @pytest.mark.skipif(not HAS_PYMUPDF, reason="PyMuPDF not installed")
    def test_non_caption_text(self):
        """Test that non-caption text doesn't match."""
        extractor = PDFImageExtractor.__new__(PDFImageExtractor)
        extractor._doc = None
        extractor._fitz = None

        patterns = extractor.CAPTION_PATTERNS

        non_captions = [
            "This is regular text",
            "The figure shows something",
            "As shown in the image above",
        ]

        for text in non_captions:
            matched = any(p.match(text) for p in patterns)
            assert not matched, f"Pattern should not match: {text}"
