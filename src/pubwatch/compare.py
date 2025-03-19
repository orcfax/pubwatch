"""Less simple Feed comparison functions."""

# pylint: disable=R0913,E0401

import logging
import time
from datetime import datetime, timezone

try:
    import objects
except ModuleNotFoundError:
    try:
        from src.pubwatch import objects
    except ModuleNotFoundError:
        from pubwatch import objects


logger = logging.getLogger(__name__)


def get_feed_id(feed_name: str):
    """Retrieve a simplified feed ID."""
    return (feed_name.rsplit("/", 1)[0]).upper()


def get_on_chain_time(feed_time: str) -> int:
    """Retrieve on-chain time in seconds (from milliseconds on-chain)."""
    return int(int(feed_time) / 1000)


def collate_latest_timestamps(on_chain_feed_data: list) -> dict:
    """Retrieve all the smallest intervals for all the feeds."""
    res = {}
    for item in on_chain_feed_data:
        feed = get_feed_id(item[0]).upper()
        on_chain_time = get_on_chain_time(item[1])
        try:
            res[feed] = on_chain_time if res[feed] < on_chain_time else res[feed]
        except KeyError:
            res[feed] = on_chain_time
    logger.info("existing on-chain feeds to compare: %s", len(set(res)))
    return res


def current_hour_rounder() -> int:
    """Rounds down to the previous hour based on the current time and
    returns a timestamp.

    NB. for logging purposes, make sure we are always using UTC.
    """
    curr_time = int(time.time())
    now_dt = datetime.fromtimestamp(curr_time, tz=timezone.utc)
    prev_hour = now_dt.replace(
        second=0, microsecond=0, minute=0, hour=now_dt.hour, tzinfo=timezone.utc
    )
    logger.debug("current hour rounder: %s", prev_hour)
    return int(prev_hour.timestamp())


def chain_hour_rounder(value: int) -> int:
    """Round an arbitrary hour number down...

    NB. for logging purposes, make sure we are always using UTC.
    """
    then_dt = datetime.fromtimestamp(value, tz=timezone.utc)
    prev_hour = then_dt.replace(
        second=0, microsecond=0, minute=0, hour=then_dt.hour, tzinfo=timezone.utc
    )
    logger.debug("chain hour rounder: %s", prev_hour)
    return int(prev_hour.timestamp())


def hour_delta_threshold(latest_timestamp: int, interval: int, threshold: int):
    """
    1. last hour, e.g. 1601 becomes 1600
    2. last hour according to on-chain, e.g. onchain 1545 becomes 1500.
    3. is 1600 - 1500 greater or less than interval, e.g. 7200 (2 hours)? no. dont publish.
    4. is 1600 - 1500 greater or less than interval, e.g. 3600 (1 hours)? yes. publish.
    """
    now = current_hour_rounder()
    then = chain_hour_rounder(latest_timestamp)
    logger.debug("now: '%s', then: '%s', exact diff: %s", now, then, now - then)
    logger.debug(
        "threshold: '%s', interval: '%s', new threshold: '%s'",
        interval,
        threshold,
        interval - threshold,
    )
    logger.debug("publish: '%s'", now - then >= interval - threshold)
    return now - then >= interval


def get_delta(timestamp_1: int, timestamp_2: int) -> int:
    """Return a positive delta between two values."""
    c1 = timestamp_1
    c2 = timestamp_2
    if timestamp_1 < timestamp_2:
        c1 = timestamp_2
        c2 = timestamp_1
    logger.debug(
        "diff between: '%s' and '%s' (%s)",
        c1,
        c2,
        (c1 - c2),
    )
    return c1 - c2


async def compare_hourly_intervals(
    latest_feed_timestamps: dict,
    intervals: dict,
    threshold: int,
):
    """Compare intervals based on hourly boundaries."""
    required_feeds = []
    required_feed_objs = []
    for feed, latest_timestamp in latest_feed_timestamps.items():
        logger.debug("feed: '%s', latest timestamp: '%s'", feed, latest_timestamp)
        feed_interval_obj = objects.FeedInterval()
        try:
            if feed in required_feeds:
                continue
            feed_name = objects.normalize_feed_name(feed)
            feed_interval_obj.feed_name = feed_name
            feed_interval_obj.interval = intervals[feed]
            required = hour_delta_threshold(
                latest_timestamp=latest_timestamp,
                interval=intervals[feed],
                threshold=threshold,
            )
            if not required:
                continue
            feed_interval_obj.required = True
            required_feed_objs.append(feed_interval_obj)
            required_feeds.append(feed)
            continue
        except KeyError:
            logger.info("feed: '%s' not being monitored", feed)
    return required_feed_objs


def make_feed_interval_obj(
    curr_time: int,
    on_chain_timestamp: int,
    threshold: int,
    interval: int,
) -> objects.FeedInterval:
    """Create a feed interval object.

    NB. function helps with better unit testing on-top of the different
    integration tests we have.
    """
    time_elapsed = get_delta(curr_time, on_chain_timestamp)
    total_time_elapsed = (
        time_elapsed + threshold
    )  # threshold increases time lapsed sensitivity.

    time_left = (interval - threshold) - time_elapsed

    feed_interval_obj = objects.FeedInterval()
    feed_interval_obj.interval = interval

    feed_interval_obj.time_left = time_left

    feed_interval_obj.elapsed = time_elapsed
    feed_interval_obj.total_time_elapsed = total_time_elapsed
    return feed_interval_obj


async def compare_direct_intervals(
    latest_feed_timestamps: dict,
    intervals: dict,
    threshold: int,
) -> list:
    """Compare intervals entirely based on their configured intervals
    and on-chain timestamps.
    """
    curr_time = int(time.time())
    required_feeds = []
    required_feed_objs = []
    for feed, on_chain_timestamp in latest_feed_timestamps.items():
        try:
            interval = intervals[feed]
        except KeyError:
            continue
        feed_interval_obj = make_feed_interval_obj(
            curr_time=curr_time,
            on_chain_timestamp=on_chain_timestamp,
            threshold=threshold,
            interval=interval,
        )
        try:
            if feed in required_feeds:
                # Feeds appear multiple times on-chain over the course
                # of a number of hours.
                continue
            logger.debug(
                "interval: '%s' elapsed: '%s', delta+threshold: '%s'",
                intervals[feed],
                feed_interval_obj.elapsed,
                (feed_interval_obj.total_time_elapsed),
            )
            feed_name = objects.normalize_feed_name(feed)
            feed_interval_obj.feed_name = feed_name
            if intervals[feed] < (feed_interval_obj.elapsed):
                logger.info(
                    "feed: '%s' out of date, elapsed: '%s', on-chain timestamp: '%s'",
                    feed,
                    feed_interval_obj.total_time_elapsed,
                    on_chain_timestamp,
                )
                feed_interval_obj.required = True
            required_feed_objs.append(feed_interval_obj)
            required_feeds.append(feed)
            continue
        except KeyError:
            logger.info("feed: '%s' not being monitored", feed)
    return required_feed_objs


async def compare_intervals(
    intervals: dict,
    comparison_data: list,
    threshold: int,
    hour_boundary: bool = False,
    batching: bool = False,
    batch_time: int = 0,
) -> list:
    """Compare feed intervals with what we have on-chain and return a
    list of gaps.
    """
    latest_feed_timestamps = collate_latest_timestamps(
        on_chain_feed_data=comparison_data
    )
    logger.debug("on-chain timestamps; %s", latest_feed_timestamps)
    if hour_boundary:
        logger.debug("comparing based on hourly boundaries")
        required_feeds = await compare_hourly_intervals(
            latest_feed_timestamps=latest_feed_timestamps,
            intervals=intervals,
            threshold=threshold,
        )
        feeds_to_request = objects.feed_list(required_feeds)
        return feeds_to_request
    logger.debug("comparing intervals directly with timestamp")
    required_feeds = await compare_direct_intervals(
        latest_feed_timestamps=latest_feed_timestamps,
        intervals=intervals,
        threshold=threshold,
    )
    to_request = [feed.feed_name for feed in required_feeds if feed.required is True]
    if batching:
        to_request = to_request + objects.feed_list_expiring(required_feeds, batch_time)
    to_request = list(set(to_request))
    logger.debug("feeds to request: '%s'", to_request)
    return to_request
