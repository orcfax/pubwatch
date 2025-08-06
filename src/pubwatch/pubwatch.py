"""Inspect Orcfax publications posted within the last hour and
requests new prices if they are needed.

The script is intended to plug publication gaps and raise the overall
reliability of the solution. It is a front-line approach with
monitoring anticipated to pick up where pubwatch leaves off.

Feeds: https://github.com/orcfax/cer-feeds/main/feeds/cer-feeds.json
"""

# pylint: disable=R0913

import argparse
import asyncio
import json
import logging
import logging.handlers
import os
import ssl
import sys
from typing import Final

import certifi

# pylint: disable=E0401
import websockets

try:
    import compare
    import feed_helper
    import kupo
    import price_monitor
except ModuleNotFoundError:
    try:
        from src.pubwatch import compare, feed_helper, kupo, price_monitor
    except ModuleNotFoundError:
        from pubwatch import compare, feed_helper, price_monitor


logging.basicConfig(
    format="%(asctime)-15s %(levelname)s :: %(filename)s:%(lineno)s:%(funcName)s() :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
    handlers=[
        logging.handlers.WatchedFileHandler("monitor.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


# Get our environment variables.
VALIDATOR_URI: Final[str] = os.environ.get("ORCFAX_VALIDATOR")
FSP_POLICY: Final[str] = os.environ.get("FSP_POLICY")
VALIDITY_TOKEN: Final[str] = os.environ.get("VALIDITY_TOKEN")

# Construct validator URI.
VALIDATION_REQUEST_URI: Final[str] = f"{VALIDATOR_URI}validate_on_demand/"

# Interval threshold to compare on-chain time with the configured
# interval.
INTERVAL_THRESHOLD: Final[str] = 1

# Default value to use when batching is configured. (900s == 15 minutes).
BATCH_DEFAULT: Final[int] = 900


def get_user_agent() -> str:
    """Return a user-agent string to connect to the monitor websocket."""
    return "orcfax-pubwatch/0.0.0"


async def connect_to_websocket(ws_uri: str, msg_to_send: str, local: bool):
    """Connect to the websocket and parse the response."""
    validator_connection = ws_uri
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    if local:
        ssl_context = None
    try:
        # pylint: disable=E1101
        async with websockets.connect(
            validator_connection,
            user_agent_header=get_user_agent(),
            ssl=ssl_context,
        ) as websocket:
            logger.info("connected to websocket")
            await websocket.send(msg_to_send)
            logger.info(msg_to_send)
            msg = await websocket.recv()
            try:
                return json.loads(msg)
            except json.JSONDecodeError:
                pass
            return msg
    except websockets.exceptions.InvalidURI as err:
        logger.error(
            "ensure 'ORCFAX_VALIDATOR' environment variable is set: %s (`export ORCFAX_VALIDATOR=wss://`)",
            err,
        )
        sys.exit(1)
    except TypeError as err:
        logger.error("ensure data is sent as JSON: %s", err)
    except (websockets.exceptions.ConnectionClosedError,) as err:
        logger.warning(
            "closed connection error '%s', attempting exponential retry: %s",
            ws_uri,
            err,
        )
    except json.decoder.JSONDecodeError as err:
        logger.error("json error decoding server response '%s': %s", msg, err)
    except websockets.exceptions.ConnectionClosedOK as err:
        logger.error("connection to: '%s' made: %s", ws_uri, err)


async def request_new_prices(pairs_to_request: dict, local: bool):
    """Send a validation request to the server to ask for a new price
    to be placed on-chain.
    """
    validate_uri = f"{VALIDATION_REQUEST_URI}"
    await connect_to_websocket(validate_uri, pairs_to_request, local)
    return


async def retrieve_feeds_intervals(feeds_file: str) -> dict:
    """Create a dict of feeds and intervals."""
    feeds = await feed_helper.read_feeds_file(feeds_file=feeds_file)
    intervals = {}
    for feed in feeds:
        if feed.interval == 0:
            # Nullify the feed if it doesn't have a valid interval.
            continue
        intervals[f"{feed.type}/{feed.pair}"] = feed.interval
    return intervals


async def compare_gaps_by_label(feeds: dict, on_chain_data: list[list]) -> list:
    """Compare publication gaps based on label and not interval. These
    will always need to be requested in any case.

    NB. currently assumes ALL feeds in cer-feeds.json are required and
    will need to be modified to ignore inactive feeds at some point if
    the nomenclature is added.
    """
    requested = []
    on_chain = []
    for feed in feeds.keys():
        requested.append(feed.upper())
    for feed in on_chain_data:
        on_chain.append(compare.get_feed_id(feed[0]).upper())
    feeds_missing = set(requested).difference(set(on_chain))
    required = []
    for item in feeds_missing:
        required.append(item.split("/")[1])
    return required


async def remove_known_from_feed_list(
    label_based_gaps: list, on_chain: list[list]
) -> list[dict]:
    """Simply remove the items we already MUST publish from the
    existing feed_list. Leaving only the pairs that will have their
    intervals compared.
    """
    for item in on_chain:
        feed = item[0]
        feed_id = compare.get_feed_id(feed).upper().split("/")[1]
        if feed_id not in label_based_gaps:
            continue
        logger.debug("removing from interval comparison: '%s'", feed_id)
        on_chain.remove(item)
    return on_chain


async def pubwatch(
    feeds_file: str,
    local: bool = False,
    nopublish: bool = False,
    threshold: int = 0,
    hour_boundary: bool = True,
    batching: bool = True,
    batch_time: int = 0,
) -> None:
    """Compare feed data with what should be published and request new
    feeds to be put on-chain if they're missing.

    1. get feeds, and policy ID.
    2. determine interval based on config.
    3. retrieve on-chain values for comparison.

    """
    _ = await kupo.get_slot()
    intervals = await retrieve_feeds_intervals(
        feeds_file=feeds_file,
    )
    fs_policy_id = await kupo.get_policy_from_fsp(
        fsp_policy_id=kupo.FSP_POLICY,
        validity_token_name=kupo.VALIDITY_TOKEN,
    )
    logger.info("fs policy ID: '%s'", fs_policy_id)
    on_chain_feed_data = await kupo.get_latest_feed_data(
        fs_policy_id=fs_policy_id,
    )
    logger.info("no. unspent datum: '%s'", len(on_chain_feed_data))
    label_based_gaps = await compare_gaps_by_label(intervals, on_chain_feed_data)
    logger.info("missing feeds based on label: %s", label_based_gaps)
    comparison_data = await remove_known_from_feed_list(
        label_based_gaps, on_chain_feed_data
    )
    pairs_to_request = await compare.compare_intervals(
        intervals=intervals,
        comparison_data=comparison_data,
        threshold=threshold,
        hour_boundary=hour_boundary,
        batching=batching,
        batch_time=batch_time,
    )
    if not label_based_gaps and not pairs_to_request:
        logger.info("no new pairs needed on-chain...")
        return
    logger.debug("label gaps: %s", label_based_gaps)
    logger.debug("time gaps: %s", pairs_to_request)
    pairs_to_request = pairs_to_request + label_based_gaps
    logger.info("we need to request the following feeds: %s", pairs_to_request)
    req = json.dumps({"feeds": pairs_to_request})
    if not nopublish:
        await request_new_prices(req, local)
        return
    logger.info("no publish flag is set, returning from script...")
    return


def handle_args() -> argparse.Namespace:
    """Handle pubwatch args and return to caller."""
    parser = argparse.ArgumentParser(
        prog="pubwatch",
        description="inspects prices on-chain and looks for anything not posted at the top of the last hour and publishes it",
        epilog="for more information visit https://orcfax.io",
    )
    parser.add_argument(
        "--local",
        help="run code locally without ssl",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--feeds",
        help="feed data describing feeds being monitored (CER-feeds (JSON))",
        required=True,
    )
    parser.add_argument(
        "--nopublish",
        help="provide a way of running this script's logic without publishing",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--hour-boundary",
        help="use an hourly boundary for publication (default: interval)",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--threshold",
        help="configure the timing threshold, e.g. for use with cron + hourly",
        type=int,
        required=False,
        default=INTERVAL_THRESHOLD,
    )
    parser.add_argument(
        "--batching",
        help="batching logic for nearly expired feeds",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--batch-time",
        help="batching time for nearly expired feeds (default: 15 minutes)",
        required=False,
        type=int,
        default=BATCH_DEFAULT,
    )
    parser.add_argument(
        "--price-monitor",
        help="monitor for price deviations and publish if necessary",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--kupo",
        help="use kupo to monitor price deviations",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="set DEBUG log level (default: INFO)",
        required=False,
        action="store_true",
    )
    return parser.parse_args()


def set_logging(args: argparse.Namespace):
    """Set logging."""
    logging.getLogger().setLevel(
        logging.DEBUG if args.debug else logging.INFO,
    )
    # Make sure urlib3 is quiet.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    # Feedback for the user if debug is on.
    logger.debug("debug logging: enabled")


def main():
    """Primary entry point for this script."""
    hour_bound: Final[str] = "hour boundary"
    interval_bound: Final[str] = "interval boundary"
    args = handle_args()
    set_logging(args)
    if args.price_monitor:
        logger.debug("price monitor selected: returning")
        asyncio.run(
            price_monitor.price_monitor(
                feed_data=args.feeds,
                use_kupo=args.kupo,
                local=args.local,
            )
        )
        sys.exit(0)
    mode = hour_bound if args.hour_boundary is True else interval_bound
    logger.info("no publish: '%s'", args.nopublish)
    logger.info("mode: '%s' threshold; '%s'", mode, args.threshold)
    asyncio.run(
        pubwatch(
            feeds_file=args.feeds,
            local=args.local,
            nopublish=args.nopublish,
            threshold=args.threshold,
            hour_boundary=args.hour_boundary,
            batching=args.batching,
            batch_time=args.batch_time,
        )
    )


if __name__ == "__main__":
    main()
