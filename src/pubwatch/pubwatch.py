"""Inspect Orcfax publications posted within the last hour and
requests new prices if they are needed.

The script is intended to plug publication gaps and raise the overall
reliability of the solution. It is a front-line approach with
monitoring anticipated to pick up where pubwatch leaves off.

Feeds: https://github.com/orcfax/cer-feeds/main/feeds/cer-feeds.json
"""

import argparse
import asyncio
import binascii
import json
import logging
import logging.handlers
import os
import ssl
import sys
import tempfile
import time
from typing import Final, Union

import cbor2
import certifi
import requests

# pylint: disable=E0401
import websockets

try:
    import feed_helper
except ModuleNotFoundError:
    try:
        from src.pubwatch import feed_helper
    except ModuleNotFoundError:
        from pubwatch import feed_helper


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
KUPO_URL: Final[str] = os.environ.get("KUPO_URL")
FSP_POLICY: Final[str] = os.environ.get("FSP_POLICY")
VALIDITY_TOKEN: Final[str] = os.environ.get("VALIDITY_TOKEN")

# Construct validator URI.
VALIDATION_REQUEST_URI: Final[str] = f"{VALIDATOR_URI}validate_on_demand/"

# Additional vars.
SLOTFILE: Final[str] = "pubwatch_slotfile"
INTERVAL_THRESHOLD: Final[str] = 120


class PubWatchException(Exception):
    """Sensible exception to return if there's a problem with this
    script.
    """


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
    except (
        websockets.exceptions.ConnectionClosedError,
        websockets.exceptions.InvalidStatusCode,
    ) as err:
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


async def unwrap_cbor(data: cbor2.CBORTag, unwrapped: list) -> Union[list | dict]:
    """Unwrap CBOR so that it renders to the API."""
    if isinstance(data.value, dict):
        return data.value
    if not isinstance(data.value, list):
        return unwrapped
    for cbor_obj in data.value:
        if isinstance(cbor_obj, cbor2.CBORTag):
            nested = []
            unwrapped.append(nested)
            await unwrap_cbor(cbor_obj, nested)
            continue
        try:
            unwrapped.append(cbor_obj.decode())
        except AttributeError:
            unwrapped.append(cbor_obj)
        except UnicodeDecodeError:
            unwrapped.append(binascii.hexlify(cbor_obj).decode())
    return unwrapped


async def process_cbor(data: str) -> dict:
    """Process metadata CBOR and return a dict/json representation."""
    dec = binascii.a2b_hex(data)
    cbor_data = cbor2.loads(dec)
    return cbor_data


async def get_datum(datum_hash: str) -> list:
    """Get the datum from Kupo."""
    datums_url = f"{KUPO_URL}/datums/{datum_hash}"
    datum = requests.get(datums_url, timeout=30)
    res = datum.json()
    cbor = await process_cbor(res["datum"])
    unwrapped = await unwrap_cbor(cbor, [])
    return unwrapped[0]


async def get_latest_feed_data(fs_policy_id: str, created_after: int = 0):
    """Get the latest feed data for processing."""
    matches_url = (
        f"{KUPO_URL}/matches/{fs_policy_id}.*?created_after={created_after}&unspent"
    )
    matches = requests.get(matches_url, timeout=30)
    res = matches.json()
    datum_hashes = []
    for item in res:
        datum_hashes.append(item["datum_hash"])
    datum = []
    for datum_hash in datum_hashes:
        datum.append(await get_datum(datum_hash))
    return datum


async def get_policy_from_fsp(fsp_policy_id: str, validity_token_name: str):
    """List the current policy ID from the Fact Statement Pointer.

    Requires the fsp policy as input as well as the validity token
    name.

    The script will return the current fact statement policy ID.

    ```sh
    curl -s \
        "http://<kupo_url>:<port>/datums/$(curl -s "http://<kupo_url>:<port>/matches/*?policy_id=0690081bc113f74e04640ea78a87d88abbd2f18831c44c4064524230&unspent&asset_name=000de140&order=most_recent_first" \
            | jq -r .[].datum_hash)?unspent"     \
                | jq -r .[] | cbor-diag

    ```

    * Example FSP policy: `0690081bc113f74e04640ea78a87d88abbd2f18831c44c4064524230`.
    * Example validity token name: `000de140`.

    """
    matches_url = f"{KUPO_URL}/matches/*?policy_id={fsp_policy_id}&asset_name={validity_token_name}&unspent"
    matches = requests.get(matches_url, timeout=30)
    res = matches.json()
    datum_hash = res[0]["datum_hash"]
    datums_url = f"{KUPO_URL}/datums/{datum_hash}"
    datum = requests.get(datums_url, timeout=30)
    res = datum.json()
    cbor = await process_cbor(res["datum"])
    return binascii.hexlify(cbor).decode()


async def get_slot() -> str:
    """Retrieve and store slot somewhere for future reference. Return
    previous slot as a reference point for UTxO retrieval functions."""
    health = requests.get(f"{KUPO_URL}/health", timeout=30)
    slot = health.headers["X-Most-Recent-Checkpoint"]
    previous_slot = "0"
    try:
        with open(
            os.path.join(tempfile.gettempdir(), SLOTFILE), "r", encoding="utf=8"
        ) as slot_file:
            previous_slot = slot_file.read().strip()
    except FileNotFoundError:
        pass
    if int(slot) <= int(previous_slot):
        raise PubWatchException("slot hasn't changed since last update")
    with open(
        os.path.join(tempfile.gettempdir(), SLOTFILE), "w", encoding="utf-8"
    ) as slot_file:
        slot_file.write(slot)
    return previous_slot


def create_interval_dict(feeds: list) -> dict:
    """Create a dict of feeds and intervals minus the interval threshold
    which should ensure that we always have datum within an anticipated
    window.
    """
    intervals = {}
    for feed in feeds:
        if feed.interval == 0:
            # Make sure there is a way to null this value.
            continue
        intervals[f"{feed.type}/{feed.pair}"] = feed.interval - INTERVAL_THRESHOLD
    return intervals


def get_feed_id(feed_name: str):
    """Retrieve a simplified feed ID."""
    return (feed_name.rsplit("/", 1)[0]).upper()


def get_on_chain_time(feed_time: str) -> int:
    """Retrieve on-chain time."""
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
    return res


def get_delta(timestamp_1: int, timestamp_2: int):
    """Return a delta between two values."""
    if timestamp_1 > timestamp_2:
        return timestamp_1 - timestamp_2
    return timestamp_2 - timestamp_1


async def compare_intervals(intervals: dict, on_chain_feed_data: list) -> list:
    """Compare feed intervals with what we have on-chain and return a
    list of gaps.
    """
    curr_time = int(time.time())
    latest_feed_timestamps = collate_latest_timestamps(
        on_chain_feed_data=on_chain_feed_data
    )
    required_feeds = []
    for feed, timestamp in latest_feed_timestamps.items():
        delta = get_delta(curr_time, timestamp)
        try:
            if feed in required_feeds:
                continue
            if intervals[feed] < delta:
                logger.info(
                    "feed: '%s' out of date, delta: '%s', actual: '%s'",
                    feed,
                    delta,
                    timestamp,
                )
                required_feeds.append(feed)
                continue
        except KeyError:
            logger.info("feed: '%s' not being monitored", feed)
    to_request = [feed.split("/", 1)[1] for feed in required_feeds]
    return to_request


async def pubwatch(feeds_file: str, local: bool = False):
    """Compare feed data with what should be published and request new
    feeds to be put on-chain if they're missing.
    """
    _ = await get_slot()
    feeds = await feed_helper.read_feeds_file(feeds_file=feeds_file)
    fs_policy_id = await get_policy_from_fsp(
        fsp_policy_id=FSP_POLICY, validity_token_name=VALIDITY_TOKEN
    )
    logger.info("policy: %s", fs_policy_id)
    intervals = create_interval_dict(feeds)
    on_chain_feed_data = await get_latest_feed_data(fs_policy_id=fs_policy_id)
    logger.info("unspent datum: %s", len(on_chain_feed_data))
    pairs_to_request = await compare_intervals(intervals, on_chain_feed_data)
    if not pairs_to_request:
        logger.info("no new pairs needed on-chain...")
        return
    logger.info("we need to request the following feeds: %s", pairs_to_request)
    req = json.dumps({"feeds": pairs_to_request})
    await request_new_prices(req, local)


def main():
    """Primary entry point of this script."""
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
    args = parser.parse_args()
    asyncio.run(pubwatch(feeds_file=args.feeds, local=args.local))


if __name__ == "__main__":
    main()
