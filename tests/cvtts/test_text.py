import pytest

from thai_spoof.cvtts.text import (
    MMS_THAI_TEXT_VERSION,
    prepare_mms_thai_text,
    require_preserved_tokenizer_text,
)


def test_sara_am_is_expanded_at_every_occurrence() -> None:
    assert prepare_mms_thai_text("ชำระเงิน ชำระเงิน") == "ช\u0e4d\u0e32ระเงิน ช\u0e4d\u0e32ระเงิน"
    assert MMS_THAI_TEXT_VERSION == "mms_thai_sara_am_v1"


def test_tone_and_other_characters_are_preserved() -> None:
    assert prepare_mms_thai_text("น้ำ โม้ 123 ABC!") == "น้\u0e4d\u0e32 โม้ 123 ABC!"


def test_preparation_is_idempotent() -> None:
    once = prepare_mms_thai_text("ชำระเงิน")
    assert prepare_mms_thai_text(once) == once


@pytest.mark.parametrize("text", ["", " ", "\t\n"])
def test_blank_text_is_rejected(text: str) -> None:
    with pytest.raises(ValueError, match="blank"):
        prepare_mms_thai_text(text)


def test_non_string_is_rejected() -> None:
    with pytest.raises(TypeError, match="string"):
        prepare_mms_thai_text(None)


class SaraAmDroppingTokenizer:
    def prepare_for_tokenization(self, text: str) -> tuple[str, dict]:
        return text.replace("ำ", ""), {}


def test_silent_character_loss_is_rejected() -> None:
    with pytest.raises(ValueError, match="Tokenizer changed"):
        require_preserved_tokenizer_text("ชำระเงิน", SaraAmDroppingTokenizer())


def test_supported_representation_survives_tokenizer() -> None:
    require_preserved_tokenizer_text(
        prepare_mms_thai_text("ชำระเงิน"), SaraAmDroppingTokenizer()
    )
