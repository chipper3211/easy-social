from __future__ import annotations

from dataclasses import dataclass

from .extensions import db
from .models import PollOption, PollVote, Post

MAX_POLL_OPTIONS = 4
MIN_POLL_OPTIONS = 2


@dataclass(frozen=True)
class PollOptionResult:
    option: PollOption
    votes: int
    percentage: int
    selected: bool


@dataclass(frozen=True)
class PollResult:
    total_votes: int
    user_vote_option_id: int | None
    options: list[PollOptionResult]


def normalize_poll_options(values: list[str]) -> list[str]:
    options: list[str] = []
    seen: set[str] = set()
    for value in values:
        option = value.strip()
        key = option.casefold()
        if not option or key in seen:
            continue
        options.append(option[:280])
        seen.add(key)
    return options[:MAX_POLL_OPTIONS]


def validate_poll_options(options: list[str]) -> str | None:
    if not options:
        return None
    if len(options) < MIN_POLL_OPTIONS:
        return "Poll posts need at least two unique options."
    if len(options) > MAX_POLL_OPTIONS:
        return "Poll posts can include at most four options."
    return None


def add_poll_options(post: Post, options: list[str]) -> None:
    for index, body in enumerate(options, start=1):
        db.session.add(PollOption(post=post, body=body, position=index))


def poll_result(post: Post, user_id: int | None) -> PollResult | None:
    content = post.display_post
    options = list(content.poll_options)
    if not options:
        return None

    vote_counts = {option.id: 0 for option in options}
    rows = (
        db.session.query(PollVote.option_id, db.func.count(PollVote.id))
        .filter(PollVote.post_id == content.id)
        .group_by(PollVote.option_id)
        .all()
    )
    vote_counts.update({option_id: count for option_id, count in rows})
    total_votes = sum(vote_counts.values())

    user_vote = None
    if user_id is not None:
        user_vote = PollVote.query.filter_by(post_id=content.id, user_id=user_id).first()

    user_vote_option_id = user_vote.option_id if user_vote else None
    results = [
        PollOptionResult(
            option=option,
            votes=vote_counts[option.id],
            percentage=round((vote_counts[option.id] / total_votes) * 100) if total_votes else 0,
            selected=option.id == user_vote_option_id,
        )
        for option in options
    ]
    return PollResult(
        total_votes=total_votes,
        user_vote_option_id=user_vote_option_id,
        options=results,
    )
