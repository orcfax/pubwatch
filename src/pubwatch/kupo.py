"""Functions to help us interact with Kupo."""

import binascii
import logging
import logging.handlers
import os
import tempfile
from typing import Final, Union

import cbor2
import requests

logger = logging.getLogger(__name__)


KUPO_URL: Final[str] = os.environ.get("KUPO_URL")

# Additional vars.
SLOTFILE: Final[str] = "pubwatch_slotfile"


class PubWatchException(Exception):
    """Sensible exception to return if there's a problem with this
    script.
    """


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
