# DART Conversion Examples

This directory contains examples of PDF to accessible HTML conversions using DART. Each example is in its own folder with consistent naming: `source.pdf` (or `source.jpg`) for the original and `accessible.html` for the converted output.

## Examples

### nasa-nesc-2024 (Flagship Example)

A comprehensive example demonstrating DART's capabilities on a complex, multi-column NASA publication. This 76-page document includes technical reports, employee spotlights, tables, and extensive imagery.

- **Source:** [NASA Technical Reports Server](https://ntrs.nasa.gov/citations/20240010837)
- **Complexity:** High (multi-column layout, mixed content types)
- **Output:** WCAG 2.2 AA compliant (0 validation issues)

See `nasa-nesc-2024/README.md` for the complete conversion workflow.

### mistral-7b

Mistral 7B LLM architecture paper (arXiv:2310.06825). Demonstrates handling of benchmark tables, model architecture diagrams, and technical references.

### generative-powers-of-ten

Generative Powers of Ten paper (arXiv:2312.02149). A diffusion model paper with algorithm pseudocode, mathematical notation, and multi-scale image examples.

### deepseek-llm

DeepSeek LLM scaling laws paper (arXiv:2401.02954). Features extensive benchmark tables, scaling law formulas, and bilingual (English/Chinese) evaluation results.

### linear-algebra-textbook

Introduction to Linear Algebra (6th Edition) excerpt. Demonstrates handling of mathematical equations and textbook formatting with extracted images.

### arxiv-attention-mechanisms

Academic paper in arXiv format (2506.01536). Standard two-column academic paper layout.

### hobbit-ocr-demo

A scanned page from "The Hobbit" demonstrating OCR capabilities on image-based documents.

## Using These Examples

### View an Example

Open any `accessible.html` file in a browser:

```bash
# Linux
xdg-open examples/mistral-7b/accessible.html

# macOS
open examples/mistral-7b/accessible.html
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
├── README.md
├── mistral-7b/
│   ├── source.pdf
│   └── accessible.html
├── generative-powers-of-ten/
│   ├── source.pdf
│   └── accessible.html
├── deepseek-llm/
│   ├── source.pdf
│   └── accessible.html
├── nasa-nesc-2024/
│   ├── accessible.html
│   └── README.md
├── linear-algebra-textbook/
│   ├── source.pdf
│   ├── accessible.html
│   └── images/
├── arxiv-attention-mechanisms/
│   ├── source.pdf
│   └── accessible.html
└── hobbit-ocr-demo/
    ├── source.jpg
    └── accessible.html
```

## Large Files

The NASA NESC 2024 source PDF (57MB) is not tracked in git due to size. To reproduce:

1. Download from: https://ntrs.nasa.gov/citations/20240010837
2. Save to `input_pdfs/nasa_nesc_2024.pdf`
3. Run: `python convert.py input_pdfs/nasa_nesc_2024.pdf`
