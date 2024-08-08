"""Helpers for processing feed specification data."""

# pylint: disable=E0611,R0902

import json
import logging

from pydantic.dataclasses import dataclass
from pydantic.tools import parse_obj_as

logger = logging.getLogger(__name__)


@dataclass
class FeedSpec:
    pair: str
    label: str
    interval: int
    deviation: int
    source: str
    calculation: str
    status: str
    type: str = "CER"


async def read_feed_data(feed_data: str) -> list[FeedSpec]:
    """ "Read feed data into memory for use in the script."""
    feed_dict = None
    with open(feed_data, "r", encoding="utf-8") as json_feeds:
        feed_dict = json.loads(json_feeds.read())
    logger.info("cer-feeds version: %s", feed_dict["meta"]["version"])
    logger.info("number of feeds: %s", len(feed_dict["feeds"]))
    feeds = []
    for item in feed_dict["feeds"]:
        feed = parse_obj_as(FeedSpec, item)
        feeds.append(feed)
    return feeds
