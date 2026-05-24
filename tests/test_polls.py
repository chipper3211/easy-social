from __future__ import annotations

import pytest

from easy_social.extensions import db
from easy_social.models import PollOption, PollVote, Post, User
from easy_social.polls import normalize_poll_options, poll_result, validate_poll_options

pytestmark = pytest.mark.unit


def test_normalize_poll_options_removes_empty_duplicates_and_limits_to_four():
    options = normalize_poll_options(["Cats", " ", "cats", "Dogs", "Birds", "Fish", "Lizards"])

    assert options == ["Cats", "Dogs", "Birds", "Fish"]


def test_validate_poll_options_requires_at_least_two_unique_options():
    assert validate_poll_options([]) is None
    assert validate_poll_options(["Only one"]) == "Poll posts need at least two unique options."
    assert validate_poll_options(["One", "Two"]) is None


def test_poll_result_counts_votes_and_marks_current_user_selection(app):
    with app.app_context():
        alice = User(username="alice", email="alice@example.com")
        bob = User(username="bob", email="bob@example.com")
        alice.set_password("password")
        bob.set_password("password")
        post = Post(author=alice, body="Favorite color?")
        red = PollOption(post=post, body="Red", position=1)
        blue = PollOption(post=post, body="Blue", position=2)
        db.session.add_all([alice, bob, post, red, blue])
        db.session.commit()
        db.session.add_all(
            [
                PollVote(post=post, option=red, user=alice),
                PollVote(post=post, option=blue, user=bob),
            ]
        )
        db.session.commit()

        result = poll_result(post, bob.id)

        assert result is not None
        assert result.total_votes == 2
        assert [option.percentage for option in result.options] == [50, 50]
        assert [option.selected for option in result.options] == [False, True]
