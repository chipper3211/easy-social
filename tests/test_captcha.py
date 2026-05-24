from __future__ import annotations

import pytest

from easy_social.captcha import CAPTCHA_ALPHABET, create_challenge, generate_answer, normalize_answer

pytestmark = pytest.mark.unit


def test_generate_answer_uses_readable_captcha_alphabet():
    answer = generate_answer()

    assert len(answer) == 5
    assert set(answer) <= set(CAPTCHA_ALPHABET)


def test_create_challenge_renders_svg_for_expected_answer():
    challenge = create_challenge("ABCD2")

    assert challenge.answer == "ABCD2"
    assert "<svg" in challenge.svg
    assert "ABCD2" not in challenge.svg
    for character in "ABCD2":
        assert f">{character}</text>" in challenge.svg


def test_normalize_answer_is_case_and_whitespace_insensitive():
    assert normalize_answer(" ab c 12 ") == "ABC12"
