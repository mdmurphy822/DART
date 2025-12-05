# PDF Accessibility Converter

A standalone toolkit for converting PDF documents to WCAG 2.1 AA compliant accessible HTML.

## Features

- **pdftotext extraction** for born-digital PDFs (best quality)
- **OCR fallback** for scanned documents using Tesseract
- **Automatic structure detection** - headings, paragraphs, tables, references
- **WCAG 2.1 AA compliant output** including:
  - Skip links for keyboard navigation
  - ARIA landmarks and roles
  - Semantic HTML structure
  - Dark mode support (via `prefers-color-scheme`)
  - Reduced motion support (via `prefers-reduced-motion`)
  - Responsive design
  - Print styles

## Installation

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt install poppler-utils tesseract-ocr

# macOS
brew install poppler tesseract
```

### Python Package

```bash
cd PDF_Accessibility_Converter

# Basic installation
pip install -e .

# With OCR support
pip install -e ".[ocr]"

# Full installation (all features)
pip install -e ".[full]"
```

## Usage

### Command Line

```bash
# Basic conversion
python convert.py document.pdf

# Specify output directory
python convert.py document.pdf -o ./accessible/

# With verbose output
python convert.py document.pdf -v

# For scanned PDFs with OCR
python convert.py scanned.pdf --dpi 400
```

### Python API

```python
from pdf_converter import convert, PDFToAccessibleHTML

# Simple conversion
result = convert('document.pdf')
if result.success:
    print(f"Saved to: {result.html_path}")
    print(f"Title: {result.title}")
    print(f"Pages: {result.pages_processed}")

# Custom configuration
converter = PDFToAccessibleHTML(dpi=400, lang='deu')
result = converter.convert('german_doc.pdf', output_dir='./output/')
```

### WCAG Enhancement Only

If you already have HTML and want to enhance it for accessibility:

```python
from pdf_converter import enhance_html_wcag, WCAGOptions

html_content = open('document.html').read()
enhanced = enhance_html_wcag(html_content, WCAGOptions(
    add_skip_link=True,
    dark_mode=True,
    add_aria_landmarks=True
))
```

## Gold Standard Template

The `templates/gold_standard.html` file demonstrates the target output format with:
- Complete semantic HTML5 structure
- ARIA roles and landmarks
- Accessible tables with proper headers
- Skip links for keyboard navigation
- Dark mode CSS support
- Responsive design
- Print-friendly styles

Use this as a reference when customizing output styles.

## Directory Structure

```
PDF_Accessibility_Converter/
├── convert.py              # CLI entry point
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── pdf_converter/          # Core package
│   ├── __init__.py         # Public API
│   ├── converter.py        # PDF to HTML converter
│   ├── wcag_enhancer.py    # WCAG enhancement
│   └── cli.py              # CLI implementation
├── templates/
│   └── gold_standard.html  # Reference template
├── output/                 # Default output directory
└── tests/
    └── test_converter.py   # Tests
```

## CLI Options

```
Usage: python convert.py <input.pdf> [options]

Options:
  -o, --output DIR    Output directory (default: ./output/)
  -n, --name NAME     Output filename (default: derived from PDF)
  --no-dark-mode      Disable dark mode CSS support
  --no-ocr            Skip OCR fallback for image-heavy PDFs
  --dpi N             DPI for OCR processing (default: 300)
  --lang CODE         Tesseract language code (default: eng)
  -v, --verbose       Enable verbose output
  --version           Show version information
```

## WCAG 2.1 AA Compliance

The generated HTML meets these WCAG 2.1 AA success criteria:

| Criterion | Description | Implementation |
|-----------|-------------|----------------|
| 1.3.1 | Info and Relationships | Semantic HTML, ARIA landmarks |
| 1.4.1 | Use of Color | Links underlined, not color-only |
| 1.4.3 | Contrast (Minimum) | 4.5:1 text contrast ratio |
| 1.4.10 | Reflow | Responsive design, no horizontal scroll |
| 2.1.1 | Keyboard | All interactive elements keyboard-accessible |
| 2.4.1 | Bypass Blocks | Skip link to main content |
| 2.4.2 | Page Titled | Meaningful page title |
| 2.4.6 | Headings and Labels | Descriptive headings |
| 2.4.7 | Focus Visible | Clear focus indicators |
| 2.3.3 | Animation | Reduced motion support |

## Integration with OSCQR

This tool can be used standalone or integrated with the OSCQR course evaluation system:

```python
# From OSCQR
from pdf_conversion import get_standalone_converter

converter_cls = get_standalone_converter()
if converter_cls:
    converter = converter_cls()
    result = converter.convert('syllabus.pdf')
```

## License

MIT License
