# Poll Post Database Design

Poll posts reuse the existing `post` table as the root content record. A post becomes a poll when it has two to four related `poll_option` rows. User votes are stored in `poll_vote`.

## Tables

### `post`

Existing table for all feed content.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Primary key | Poll options reference this value. |
| `body` | Text | Not null, default `""` | Optional poll question or context. |
| `media_filename` | String(255) | Nullable | Poll posts may still include media. |
| `media_type` | String(20) | Nullable | Existing image/video discriminator. |
| `created_at` | DateTime(timezone=True) | Not null, indexed | Sorts feed content. |
| `author_id` | Integer | Foreign key to `user.id`, indexed | Poll creator. |
| `repost_of_id` | Integer | Foreign key to `post.id`, nullable, indexed | Reposts display the original poll. |

### `poll_option`

Stores the answer choices for a poll post.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Primary key | Vote records reference this value. |
| `post_id` | Integer | Foreign key to `post.id`, not null, indexed | Parent poll post. |
| `body` | String(280) | Not null, check `length(body) > 0` | User-visible option text. |
| `position` | Integer | Not null, check `1 <= position <= 4` | Stable display order. |

Constraints:

- `uq_poll_option_position` prevents duplicate option positions inside the same poll.
- Application validation requires at least two unique non-empty options and stores at most four options.

Relationship:

- `post.poll_options` is a one-to-many relationship ordered by `position`.

### `poll_vote`

Stores each user's vote in a poll.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Primary key | Internal vote identifier. |
| `post_id` | Integer | Foreign key to `post.id`, not null, indexed | Poll being voted on. |
| `option_id` | Integer | Foreign key to `poll_option.id`, not null, indexed | Selected option. |
| `user_id` | Integer | Foreign key to `user.id`, not null, indexed | Voter. |
| `created_at` | DateTime(timezone=True) | Not null | Vote timestamp. |

Constraints:

- `uq_poll_vote_user_post` allows each user to vote only once per poll.

Relationships:

- `poll_vote.post_id` links votes to the poll post for aggregate counts.
- `poll_vote.option_id` links each vote to the selected option.
- `poll_vote.user_id` links each vote to the voter.

## Result Calculation

The application counts `poll_vote` rows grouped by `option_id`, sums all rows for `total_votes`, then calculates each option percentage as `round(option_votes / total_votes * 100)`. Before a user votes, the post displays option buttons. After a user votes, the same post displays percentages, vote counts, and the user's selected option.
