"""Price monitoring functionality, e.g. for price deviations.

Price monitor code uses a robust loop to check for updates every
`<configured>` seconds. Functionality works best when paired with a
connection to Kupo where it is possible to check prices on-chain. If
Kupo isn't available, it can use data from its connection to the
Orcfax validator database.
"""

# pylint: disable=R0914

import json
import logging
import os
import ssl
import sys
import time
from typing import Final

import certifi
import websockets
from tenacity import retry, wait_exponential

try:
    import compare
    import feed_helper
    import kupo
except ModuleNotFoundError:
    try:
        from src.pubwatch import compare, feed_helper, kupo
    except ModuleNotFoundError:
        from price_monitor import compare, feed_helper, kupo


logger = logging.getLogger(__name__)

KUPO_URL: Final[str] = os.environ.get("KUPO_URL")
VALIDATOR_URL: Final[str] = os.environ.get("ORCFAX_VALIDATOR")
MONITOR_URL: Final[str] = f"{VALIDATOR_URL}price_monitor/"
VALIDATION_REQUEST_URL: Final[str] = f"{VALIDATOR_URL}validate_on_demand/"

# Seconds after which to request current price off-chain.
POLLING_TIME: Final[int] = 60

# Decimal places to round deviation to before comparison.
DECIMAL_PLACES: Final[int] = 2


def get_user_agent() -> str:
    """Return a user-agent string to connect to the monitor websocket."""
    return "orcfax-price-monitor/0.0.0"


def _retry_logging(retry_state):
    """Provide some logging about tenacity retry attempts."""
    logger.info(
        "attempting connection to validator websocket '%s' (tries: %s)",
        f"{MONITOR_URL}",
        retry_state.attempt_number,
    )


@retry(wait=wait_exponential(multiplier=1, min=4, max=30), after=_retry_logging)
async def connect_to_websocket(ws_url: str, msg_to_send: str, local: bool = False):
    """Connect to the websocket and parse the response."""
    validator_connection = ws_url
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    if local:
        ssl_context = None
    try:
        async with websockets.connect(
            validator_connection,
            user_agent_header=get_user_agent(),
            ping_timeout=None,
            ssl=ssl_context,
        ) as websocket:
            logger.info("connected to websocket")
            await websocket.send(msg_to_send)
            logger.info("sending request: %s", msg_to_send)
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
            ws_url,
            err,
        )
        if ws_url == MONITOR_URL:
            # Only raise an exception if the problem exists with the
            # monitor function.
            raise err
    except json.decoder.JSONDecodeError as err:
        logger.error("json error decoding server response '%s': %s", msg, err)
    except websockets.exceptions.ConnectionClosedOK as err:
        logger.error("connection to: '%s' made: %s", ws_url, err)
    return {}


def orcfax_round(value: float):
    """Wrapper for round in case we ever change our strategy here."""
    return round(value, DECIMAL_PLACES)


def determine_deviation(values: list[float]) -> float:
    """Determine if there is a percentage deviation between two numbers
    for a given threshold, default=0.1  (1%).
    """
    if not values:
        # There are no values to compare.
        return 0.0
    percentage = abs(((values[1] - values[0]) / values[0]) * 100)
    return orcfax_round(percentage)


async def get_latest_collected(
    monitor_url: str, feeds_to_request: dict, local: bool = False
):
    """Using the montioring endpoint list only the latest collected."""
    data = await connect_to_websocket(monitor_url, feeds_to_request, local)
    if data.get("error"):
        logger.error("error in websocket response: %s", data.get("error"))
        return
    latest_collected = {}
    for item in data.get("data", []):
        pair = list(item.keys())[0]
        if pair not in feeds_to_request:
            continue
        values = list(item.values())[0]
        if not values:
            continue
        latest_collected[pair] = values[1]
    return latest_collected


async def collate_kupo_data(on_chain_feed_data: dict, latest_collected: dict):
    """Collate kupo data and forrmat it against known structures."""
    latest_prices_on_chain = compare.collate_latest_prices(
        on_chain_feed_data=on_chain_feed_data
    )
    comparison_data = []
    for key, value in latest_prices_on_chain.items():
        pair = key.replace("CER/", "")
        on_chain_latest = value[1]
        if pair not in latest_collected:
            continue
        latest_available = latest_collected[pair]
        comparison_data.append({pair: [on_chain_latest, latest_available]})
    return comparison_data


async def compare_validator_data_deviations(feeds: dict, data: dict):
    """Compare data from the Orcfax validator and return a list of
    feeds to request if needed.

    Example datta from the validator. We have aa list of feeds and
    their deviations. LH == published price, RH == latest unpublished
    price.

    ```json
        {
            "error": null,
            "data": [{
                "ADA-USD": [0.256395, 0.256463]
            }]
        }
    ```

    """
    deviations = {}
    for feed in feeds:
        deviations[feed.pair] = feed.deviation
    pairs_to_request = []
    for item in data["data"]:
        pair = list(item.keys())[0]
        if pair not in deviations:
            continue
        values = list(item.values())[0]
        logger.info("comparing; %s (%s)", pair, values)
        if not values:
            continue
        deviation = determine_deviation(values)
        logger.info(
            "%s calculated as: %s%% from %s (threshold: %s%%)",
            pair,
            deviation,
            values,
            deviations[pair],
        )
        if deviation < deviations[pair]:
            continue
        logger.info(
            "requesting: %s (deviation: %s actual: %s)",
            pair,
            deviations[pair],
            deviation,
        )
        pairs_to_request.append(pair)
    return {"feeds": pairs_to_request}


async def request_new_prices(pairs_to_request: dict, local: bool = False):
    """Send a validation request to the server to ask for a new price
    to be placed on-chain.
    """
    validate_url = f"{VALIDATION_REQUEST_URL}"
    await connect_to_websocket(validate_url, json.dumps(pairs_to_request), local)
    return


async def request_deviations_ws(
    monitor_url: str, feeds: dict, nopublish: bool, local: bool = False
):
    """Request published_unpublished prices for the feeds in our
    given feeds list from the websocket. Work out deviation and
    request the required values.
    """
    feeds_to_request = json.dumps({"feed_ids": [feed.pair for feed in feeds]})
    data = await connect_to_websocket(monitor_url, feeds_to_request, True)
    if data.get("error"):
        logger.error("error in websocket response: %s", data.get("error"))
        return
    pairs_to_request = await compare_validator_data_deviations(feeds, data)
    if not pairs_to_request.get("feeds"):
        logger.info("not requesting any updated pairs from websocket...")
        return
    if not nopublish:
        await request_new_prices(pairs_to_request=pairs_to_request, local=local)
        return
    logger.info("no publish flag is set, returning from script...")
    return


async def request_deviations_kupo(
    monitor_url: str, feeds: dict, nopublish: bool, local: bool = False
):
    """Request published_unpublished prices for the feeds in our
    given feeds list from kupo. Work out deviation and request
    the required values.
    """
    logging.info("using kupo for price-monitoring")
    try:
        _ = await kupo.get_slot(price_monitor=True)
    except kupo.KupoError as err:
        raise kupo.KupoError(f"{err}") from err
    except kupo.PubWatchException:
        # Return this time as another process (pubwatch) has likely
        # just checked Kupo and we don't need to double our effort.
        return
    fs_policy_id = await kupo.get_policy_from_fsp(
        fsp_policy_id=kupo.FSP_POLICY,
        validity_token_name=kupo.VALIDITY_TOKEN,
    )
    logger.info("fs policy ID: '%s'", fs_policy_id)
    feeds_to_request = json.dumps({"feed_ids": [feed.pair for feed in feeds]})
    latest_collected = await get_latest_collected(monitor_url, feeds_to_request, local)
    if not latest_collected:
        return
    on_chain_feed_data = await kupo.get_latest_feed_data(fs_policy_id=fs_policy_id)
    comparison_data = await collate_kupo_data(on_chain_feed_data, latest_collected)
    pairs_to_request = await compare_validator_data_deviations(
        feeds, {"error": None, "data": comparison_data}
    )
    if not pairs_to_request.get("feeds"):
        logger.info("not requesting any updated pairs from kupo...")
        return
    logger.info("pairs to request: %s", pairs_to_request)
    if not nopublish:
        await request_new_prices(pairs_to_request=pairs_to_request, local=local)
        return
    logger.info("no publish flag is set, returning from script...")
    return


async def price_monitor(
    feed_data: str, use_kupo: bool, nopublish: bool, local: bool = False
):
    """Monitor prices on-chain and update based on `feed_data`."""
    monitor_url = MONITOR_URL
    feeds = await feed_helper.read_feeds_file(feeds_file=feed_data)
    try:
        while True:
            if not use_kupo:
                await request_deviations_ws(
                    monitor_url=monitor_url,
                    feeds=feeds,
                    nopublish=nopublish,
                    local=local,
                )
            else:
                try:
                    await request_deviations_kupo(
                        monitor_url=monitor_url,
                        feeds=feeds,
                        nopublish=nopublish,
                        local=local,
                    )
                except kupo.KupoError as err:
                    logger.error(
                        "problem connecting to kupo falling back on websocket: %s", err
                    )
                    await request_deviations_ws(monitor_url, feeds, nopublish, local)
            logging.info("going to sleep, polling in: '%s' seconds", POLLING_TIME)
            time.sleep(POLLING_TIME)
            continue
    except KeyboardInterrupt:
        print("", file=sys.stderr)
        logger.info("exiting...")
