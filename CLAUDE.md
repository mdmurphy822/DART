# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install (choose one)
pip install -e .              # Basic installation
pip install -e ".[ocr]"       # With OCR support
pip install -e ".[full]"      # All features
pip install -e ".[dev]"       # Development with testing tools

# Run converter
python convert.py document.pdf                    # Basic conversion
python convert.py document.pdf -o ./accessible/  # Specify output dir
python convert.py scanned.pdf --dpi 400          # OCR for scanned PDFs

# Testing
pytest                        # Run all tests
pytest tests/test_converter.py -v  # Run single test file with verbose output

# Linting/Formatting
black .                       # Format code (line-length: 100)
ruff check .                  # Lint code
```

## System Dependencies

Requires `poppler-utils` (for pdftotext/pdfinfo) and optionally `tesseract-ocr` for OCR fallback.

## Architecture Overview

The converter follows a pipeline architecture: **PDF → Text Extraction → Structure Detection → Semantic HTML → WCAG 2.2 Enhancement → Validation**

### Core Modules

- **`pdf_converter/converter.py`** (`PDFToAccessibleHTML`): Main conversion pipeline
  - Uses `pdftotext` for born-digital PDFs (primary), falls back to Tesseract OCR for scanned documents
  - `_structure_text()`: Parses raw text into `TextBlock` objects (paragraph/heading detection)
  - `_generate_semantic_html()`: Creates initial HTML with sections and proper heading hierarchy
  - Returns `ConversionResult` dataclass with success status, output path, metadata, and WCAG validation results

- **`pdf_converter/wcag_enhancer.py`** (`WCAGHTMLEnhancer`): Post-processor for WCAG 2.2 AA compliance
  - Six-phase enhancement: document structure → semantic improvements → figures → cross-references → CSS → cleanup
  - Adds skip links, ARIA landmarks, section wrappers, expandable figure descriptions
  - Detects and converts references sections to ordered lists, table-like content to proper tables
  - Creates internal links for "Figure X" and "Table X" references
  - `WCAGOptions` dataclass controls which enhancements to apply
  - **WCAG 2.2 specific features:**
    - Focus not obscured (2.4.11, 2.4.12): scroll-margin for focused elements
    - Focus appearance (2.4.13): 3px outline exceeds 2px minimum requirement
    - Target size (2.5.8): 24x24px minimum for interactive elements

- **`pdf_converter/wcag_validator.py`** (`WCAGValidator`): WCAG 2.2 AA validation
  - Validates HTML against 13 WCAG success criteria
  - Reports issues by severity: CRITICAL (Level A), HIGH (Level AA), MEDIUM (best practice), LOW (enhancement)
  - `ValidationReport` dataclass with JSON and text output formats
  - Integrated into converter pipeline (optional, enabled by default)

### Public API

```python
from pdf_converter import convert, PDFToAccessibleHTML, enhance_html_wcag, WCAGOptions
from pdf_converter import WCAGValidator, validate_html_wcag, ValidationReport
```

The `convert()` function in `__init__.py` is the simple entry point; `PDFToAccessibleHTML` allows custom configuration (dpi, lang, min_confidence, validate_wcag).

### Key Design Patterns

- Heading detection uses Roman numerals (I., II.), numbered sections (1., 1.1), and ALL CAPS patterns
- `_split_heading_from_paragraph()` handles cases where OCR merges section headers with following text
- `_fix_section_headers()` repairs common OCR artifacts like "I NTRODUCTION" → "INTRODUCTION"
- Reference template at `templates/gold_standard.html` shows target output format
