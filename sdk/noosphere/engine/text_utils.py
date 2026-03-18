"""
🧠 Noosphere — Text Processing Utilities

CJK/Latin tokenizer, Jaccard similarity, and stop words.
Extracted from noosphere_mcp.py L573-L732.
"""


# Stop words for English text filtering
_STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "shall", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into",
    "about", "that", "this", "it", "its", "my", "your", "his",
    "her", "we", "they", "them", "our", "and", "or", "but", "not",
    "so", "if", "than", "then", "when", "while", "what", "how",
    "which", "who", "where", "why", "all", "each", "every", "no",
    "more", "most", "some", "any", "just", "also", "very", "too",
})


def _is_cjk(char: str) -> bool:
    """Check if a character is CJK (Chinese/Japanese/Korean)."""
    cp = ord(char)
    return (
        (0x4E00 <= cp <= 0x9FFF)       # CJK Unified Ideographs
        or (0x3400 <= cp <= 0x4DBF)    # CJK Extension A
        or (0x20000 <= cp <= 0x2A6DF)  # CJK Extension B
        or (0xF900 <= cp <= 0xFAFF)    # Compatibility Ideographs
        or (0x2F800 <= cp <= 0x2FA1F)  # Compatibility Supplement
        or (0x3000 <= cp <= 0x303F)    # CJK Symbols & Punctuation
        or (0x3040 <= cp <= 0x309F)    # Hiragana
        or (0x30A0 <= cp <= 0x30FF)    # Katakana
        or (0xAC00 <= cp <= 0xD7AF)    # Hangul Syllables
    )


def _tokenize(text: str) -> set[str]:
    """Zero-dependency tokenizer that handles both CJK and Latin text.

    For CJK text: generates character unigrams and bigrams.
    For Latin text: splits by whitespace, strips punctuation, filters short words.
    Returns a unified set of lowercase tokens for cross-language matching.
    """
    tokens: set[str] = set()
    text = text.lower()

    # Extract CJK characters and generate unigrams + bigrams
    cjk_chars: list[str] = []
    latin_buffer: list[str] = []

    for char in text:
        if _is_cjk(char):
            # Flush latin buffer
            if latin_buffer:
                word = "".join(latin_buffer).strip()
                clean = word.strip(".,;:!?\"'()[]{}·—–…")
                if len(clean) >= 3:
                    tokens.add(clean)
                latin_buffer = []
            cjk_chars.append(char)
            tokens.add(char)  # unigram
        elif char.isspace() or char in ".,;:!?\"'()[]{}·—–…":
            # Flush latin buffer as a word
            if latin_buffer:
                word = "".join(latin_buffer).strip()
                clean = word.strip(".,;:!?\"'()[]{}·—–…")
                if len(clean) >= 3:
                    tokens.add(clean)
                latin_buffer = []
            # Flush CJK buffer for continuity
            if cjk_chars:
                for i in range(len(cjk_chars) - 1):
                    tokens.add(cjk_chars[i] + cjk_chars[i + 1])  # bigram
                cjk_chars = []
        else:
            # Flush CJK buffer
            if cjk_chars:
                for i in range(len(cjk_chars) - 1):
                    tokens.add(cjk_chars[i] + cjk_chars[i + 1])
                cjk_chars = []
            latin_buffer.append(char)

    # Flush remaining buffers
    if latin_buffer:
        word = "".join(latin_buffer).strip()
        clean = word.strip(".,;:!?\"'()[]{}·—–…")
        if len(clean) >= 3:
            tokens.add(clean)
    if cjk_chars:
        for i in range(len(cjk_chars) - 1):
            tokens.add(cjk_chars[i] + cjk_chars[i + 1])

    return tokens - _STOP_WORDS


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0
