"""Block sprite + helpers.

Currently a placeholder. Future work will introduce a Block class that
tracks color/type, animation state (idle, flashing, popping, falling),
and chain ancestry so the score system can credit chained matches
correctly.
"""

from settings import BlockSettings


def random_block_type(rng) -> str:
    """Pick a random block type using the provided random.Random instance.

    Args:
        rng: A seeded ``random.Random`` so test runs stay reproducible.

    Returns:
        One of the strings in ``BlockSettings.TYPES``.
    """
    return rng.choice(BlockSettings.TYPES)


class Block:
    """A single block on the playfield.

    Stub. Real implementation will own color, animation phase, and the
    chain link pointer so the chain bonus system can walk back to the
    original clear that started the cascade.
    """

    def __init__(self, block_type: str) -> None:
        self.type = block_type
        # TODO: animation state (idle/flashing/popping/falling).
        # TODO: chain-link reference.
