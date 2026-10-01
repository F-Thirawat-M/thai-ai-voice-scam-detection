import math

import pytest

from data.exploration.typhoon_thai_dialect_isan.typhoon_eda_utils import (
    age_band, fetch_metadata, parse_age, parse_filename,
)


@pytest.mark.parametrize("value", [None, "", "abc", "nan", "inf", -1, 0, 120])
def test_invalid_ages_stay_unknown(value):
    assert parse_age(value) is None


def test_age_and_bands():
    assert parse_age("24.0") == 24
    assert [age_band(x) for x in [16, 18, 29, 30, 44, 45, 59, 60, None, math.nan]] == [
        "<18", "18-29", "18-29", "30-44", "30-44", "45-59", "45-59", "60+", "unknown", "unknown"]


def test_candidate_filename_key_is_not_imputed_demographics():
    parsed = parse_filename("opentyphoon;is;x_061;gen;0049.wav")
    assert parsed["candidate_speaker_key"] == "x_061"
    assert parsed["prompt_domain_code"] == "gen"
    assert "gender" not in parsed
    assert parse_filename("unknown.wav")["filename_parse_status"] == "unparsed"


def test_fetch_requires_pinned_revision_without_network(tmp_path):
    with pytest.raises(ValueError, match="commit SHA"):
        fetch_metadata(tmp_path, "main")
