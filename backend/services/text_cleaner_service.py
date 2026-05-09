"""
text_cleaner_service.py
-----------------------
OCR text cleaning and normalisation for Legal Metrology compliance.

Processing rules implemented:
    - Ignore OCR noise
    - Ignore unwanted symbols
    - Ignore duplicate text
    - Ignore unreadable fragments
    - Extract only meaningful legal metrology data
    - Clean and normalise extracted text
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TextCleanerService:
    """Clean and normalise OCR-extracted text for compliance analysis."""

    # Characters that are almost always OCR artefacts
    NOISE_CHARS = re.compile(r'[§¶†‡•◦◘◙►◄↕‼¶§▬↨↑↓→←∟↔▲▼|]')

    # Repeated punctuation / symbols (e.g. "---", "***", "===")
    REPEATED_SYMBOLS = re.compile(r'([^\w\s])\1{2,}')

    # Strings that are too short or purely non-alphanumeric
    MIN_MEANINGFUL_LENGTH = 2

    def clean(self, raw_text: str) -> str:
        """
        Full cleaning pipeline for raw OCR text.

        Args:
            raw_text: Raw text from OCR engine

        Returns:
            str: Cleaned, normalised text
        """
        if not raw_text:
            return ""

        text = raw_text

        # Step 1: Remove OCR noise characters
        text = self._remove_noise_chars(text)

        # Step 2: Normalise whitespace and line endings
        text = self._normalise_whitespace(text)

        # Step 3: Remove duplicate lines
        text = self._remove_duplicate_lines(text)

        # Step 4: Remove unreadable fragments
        text = self._remove_unreadable_fragments(text)

        # Step 5: Fix common OCR misreadings
        text = self._fix_common_ocr_errors(text)

        # Step 6: Normalise currency and unit symbols
        text = self._normalise_symbols(text)

        # Step 7: Final trim
        text = text.strip()

        logger.info("Text cleaned: %d → %d chars", len(raw_text), len(text))
        return text

    # ──────────────────────────────────────────────────────────────────────
    # Pipeline steps
    # ──────────────────────────────────────────────────────────────────────

    def _remove_noise_chars(self, text: str) -> str:
        """Remove non-printable and known OCR artefact characters."""
        # Remove non-printable control characters (keep \n, \r, \t)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        # Remove known noise symbols
        text = self.NOISE_CHARS.sub('', text)
        return text

    def _normalise_whitespace(self, text: str) -> str:
        """Collapse extra spaces / tabs and normalise line endings."""
        # Normalise line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Collapse multiple spaces/tabs within a line
        text = re.sub(r'[ \t]+', ' ', text)
        # Collapse more than two consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def _remove_duplicate_lines(self, text: str) -> str:
        """Remove exact duplicate lines while preserving order."""
        seen: set[str] = set()
        unique_lines: list[str] = []
        for line in text.split('\n'):
            stripped = line.strip()
            if stripped and stripped.lower() not in seen:
                seen.add(stripped.lower())
                unique_lines.append(stripped)
            elif not stripped:
                unique_lines.append('')  # preserve blank lines
        return '\n'.join(unique_lines)

    def _remove_unreadable_fragments(self, text: str) -> str:
        """Remove lines that are too short or contain mostly garbage."""
        lines = text.split('\n')
        cleaned_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Keep blank lines (paragraph separators)
            if not stripped:
                cleaned_lines.append('')
                continue

            # Remove lines shorter than minimum meaningful length
            if len(stripped) < self.MIN_MEANINGFUL_LENGTH:
                continue

            # Remove lines that are entirely special characters
            alpha_ratio = sum(c.isalnum() for c in stripped) / len(stripped)
            if alpha_ratio < 0.3:
                continue

            cleaned_lines.append(stripped)

        return '\n'.join(cleaned_lines)

    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix frequent OCR misreadings in Indian product labels."""
        replacements = [
            # MRP variants
            (r'\bM[\s.]?R[\s.]?P[\s.]?', 'MRP '),
            (r'\bMRF\b(?=\s*[₹Rs])', 'MRP'),
            (r'\bMPR\b', 'MRP'),

            # Currency
            (r'Rs[\s.]?(\d)', r'Rs. \1'),
            (r'R[sS]\.?\s*', 'Rs. '),

            # Net quantity patterns
            (r'\bNet[\s.]?Qty[\s.:]*', 'Net Quantity: '),
            (r'\bNet[\s.]?Wt[\s.:]*', 'Net Weight: '),
            (r'\bNet[\s.]?Vol[\s.:]*', 'Net Volume: '),

            # Date patterns
            (r'\bMfg[\s.]?(?:Date|Dt)[\s.:]*', 'Mfg Date: '),
            (r'\bExp[\s.]?(?:Date|Dt)[\s.:]*', 'Exp Date: '),
            (r'\bBest[\s.]?Before[\s.:]*', 'Best Before: '),
            (r'\bUse[\s.]?Before[\s.:]*', 'Use Before: '),

            # Common label terms
            (r'\bMfg[\s.]?By[\s.:]*', 'Manufactured By: '),
            (r'\bMkt[\s.]?By[\s.:]*', 'Marketed By: '),
            (r'\bImp[\s.]?By[\s.:]*', 'Imported By: '),

            # Country of origin
            (r'\bCountry\s+of\s+0rigin\b', 'Country of Origin'),
            (r'\bMade\s+[i1]n\s+', 'Made in '),

            # Batch / Lot
            (r'\bBatch[\s.]?No[\s.:]*', 'Batch No: '),
            (r'\bLot[\s.]?No[\s.:]*', 'Lot No: '),
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _normalise_symbols(self, text: str) -> str:
        """Normalise currency and unit symbols."""
        # Ensure ₹ is followed by a space
        text = re.sub(r'₹\s*', '₹ ', text)
        # Remove repeated symbols
        text = self.REPEATED_SYMBOLS.sub(r'\1', text)
        return text
