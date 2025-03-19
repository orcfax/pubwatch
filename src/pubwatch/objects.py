"""Objects and helpers used with this script to make life easier for
us.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FeedInterval:
    feed_name: str = "UNTITLED"
    elapsed: int = 0
    total_time_elapsed: int = 0
    time_left: int = 0
    interval: int = 0
    required: bool = False

    def __str__(self):
        """Provide some info about this feed object."""
        return f"feed interval obj: '{self.feed_name}', time_left: '{self.time_left}', required: '{self.required}', interval: '{self.interval}'"


def normalize_feed_name(feed: str) -> str:
    """Normalize feed name. Will raise KeyError if the args are wrong
    or incompatible.
    """
    return feed.split("/", 1)[1]


def feed_list(feeds: list[FeedInterval]):
    """Return a list of feeds that we are going to rerquest."""
    if not feeds:
        return []
    if not isinstance(feeds[0], FeedInterval):
        logger.error("feeds list is improperly formatted, check the code")
        # NB. we can return an error here. It doesn't really make a
        # difference to us right now.
        return []
    return [feed.feed_name for feed in feeds]


def feed_list_expiring(feeds: list[FeedInterval], batch_time: int):
    """Return a list of feeds that are expiring."""
    if not feeds:
        return []
    if not isinstance(feeds[0], FeedInterval):
        logger.error("feeds list is improperly formatted, check the code")
        # NB. we can return an error here. It doesn't really make a
        # difference to us right now.
        return []
    return [feed.feed_name for feed in feeds if feed.time_left - batch_time <= 0]
