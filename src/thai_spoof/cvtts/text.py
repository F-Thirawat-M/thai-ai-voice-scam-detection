"""Conservative text preparation for the pinned MMS Thai pilot.

Keep the original text in provenance. This changes only the representation of
Thai SARA AM; it does not spell-correct, remove words, or guarantee pronunciation.
"""

MMS_THAI_TEXT_VERSION = "mms_thai_sara_am_v1"


def prepare_mms_thai_text(text: str) -> str:
    """Represent U+0E33 with U+0E4D + U+0E32, supported by this tokenizer."""
    if not isinstance(text, str):
        raise TypeError("TTS text must be a string")
    if not text.strip():
        raise ValueError("TTS text must not be blank")
    return text.replace("\u0e33", "\u0e4d\u0e32")


def require_preserved_tokenizer_text(text: str, tokenizer: object) -> None:
    """Fail if this pilot's tokenizer silently changes the prepared text.

    Unknown-token counts alone do not detect characters removed before encoding.
    This intentionally fails on undeclared case/punctuation/whitespace changes
    too; broaden the preparation policy explicitly rather than silently dropping.
    """
    prepared, _ = tokenizer.prepare_for_tokenization(text)
    if prepared != text:
        raise ValueError(
            f"Tokenizer changed the prepared TTS text: {text!r} -> {prepared!r}"
        )
