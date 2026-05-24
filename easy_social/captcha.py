from __future__ import annotations

import html
import random
import secrets
from dataclasses import dataclass


CAPTCHA_SESSION_KEY = "captcha_answer"
CAPTCHA_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


@dataclass(frozen=True)
class CaptchaChallenge:
    answer: str
    svg: str


def generate_answer(length: int = 5) -> str:
    return "".join(secrets.choice(CAPTCHA_ALPHABET) for _ in range(length))


def render_svg(answer: str) -> str:
    escaped = html.escape(answer)
    rng = random.Random(answer)
    lines = "\n".join(
        f'<line x1="{rng.randint(0, 180)}" y1="{rng.randint(0, 64)}" '
        f'x2="{rng.randint(0, 180)}" y2="{rng.randint(0, 64)}" />'
        for _ in range(8)
    )
    letters = "\n".join(
        f'<text x="{28 + index * 28}" y="{rng.randint(36, 48)}" '
        f'rotate="{rng.randint(-18, 18)}">{html.escape(char)}</text>'
        for index, char in enumerate(answer)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="180" height="64" viewBox="0 0 180 64" role="img" aria-label="CAPTCHA challenge">
  <rect width="180" height="64" rx="8" fill="#eef5f6" />
  <g stroke="#89b9c1" stroke-width="1.5" opacity="0.72">
    {lines}
  </g>
  <g fill="#0b5562" font-family="Verdana, Arial, sans-serif" font-size="28" font-weight="700">
    {letters}
  </g>
  <text x="90" y="58" text-anchor="middle" fill="#64707d" font-size="10" font-family="Arial, sans-serif">Enter the characters shown</text>
</svg>"""


def create_challenge(answer: str | None = None) -> CaptchaChallenge:
    challenge_answer = (answer or generate_answer()).upper()
    return CaptchaChallenge(answer=challenge_answer, svg=render_svg(challenge_answer))


def normalize_answer(value: str) -> str:
    return "".join(value.split()).upper()
