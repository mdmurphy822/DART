# DART Conversion Examples

This directory contains examples of PDF to accessible HTML conversions using DART.

## Examples

### NASA NESC 2024 Technical Update (Flagship Example)

**Directory:** `nasa_nesc_2024/`

A comprehensive example demonstrating DART's capabilities on a complex, multi-column NASA publication. This 76-page document includes technical reports, employee spotlights, tables, and extensive imagery.

- **Source:** [NASA Technical Reports Server](https://ntrs.nasa.gov/citations/20240010837)
- **Complexity:** High (multi-column layout, mixed content types)
- **Output:** WCAG 2.2 AA compliant (0 validation issues)

See `nasa_nesc_2024/README.md` for the complete conversion workflow.

### Small Samples

**Directory:** `small_samples/`

Quick reference examples for common document types:

| File | Description |
|------|-------------|
| `Introduction_to_Linear_Algebra_6ed_accessible.html` | Math textbook with equations |
| `2506.01536v1_accessible.html` | Academic paper (arXiv format) |
| `badimage_accessible.html` | Image-only document with OCR |

Each includes the source PDF for direct comparison.

## Using These Examples

### View an Example

Open any `*_accessible.html` file in a browser to see the accessible output:

```bash
# Linux
xdg-open examples/nasa_nesc_2024/accessible.html

# macOS
open examples/nasa_nesc_2024/accessible.html
```

### Convert Your Own PDF

```bash
python convert.py your_document.pdf -o ./output/
```

### Test Accessibility

Use browser developer tools or automated tools:
- **WAVE:** wave.webaim.org
- **axe DevTools:** Browser extension
- **NVDA/VoiceOver:** Screen reader testing

## Directory Structure

```
examples/
├── README.md                 # This file
├── nasa_nesc_2024/
│   ├── README.md             # Conversion workflow documentation
│   └── accessible.html       # Final WCAG 2.2 AA output
└── small_samples/
    ├── *.pdf                 # Source PDFs
    ├── *_accessible.html     # Converted HTML files
    └── *_images/             # Extracted images
```

## Large Files

The NASA NESC 2024 source PDF (57MB) and extracted assets (~18MB images) are not tracked in git due to size. To reproduce the full conversion:

1. Download from: https://ntrs.nasa.gov/citations/20240010837
2. Save to `input_pdfs/nasa_nesc_2024.pdf`
3. Run: `python convert.py input_pdfs/nasa_nesc_2024.pdf`
