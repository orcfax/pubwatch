"""Test basic price montioring functions."""

import pytest

from src.pubwatch.feed_helper import FeedSpec
from src.pubwatch.price_monitor import (
    collate_kupo_data,
    compare_validator_data_deviations,
    determine_deviation,
)

deviation_tests = [
    (1, 2, 100),
    (2, 1, 50),
    (2, 1.96, 2),
    (27, 24.3, 10),
    (24.3, 27, 11.11),
    (24.3, 26.73, 10),
    # ADA-USD.
    (0.7691, 0.730645, 5),
    (0.807555, 0.7691, 4.76),
    # FACT-ADA.
    (0.004380, 0.0043362, 1),
    (0.0044238, 0.004380, 0.99),
    # rsERG-ADA.
    (1.2844, 1.258712, 2),
    (1.310088, 1.2844, 1.96),
]


@pytest.mark.parametrize("price_1, price_2, deviation", deviation_tests)
def test_determine_deviation(price_1, price_2, deviation):
    """Ensure that deviation is calculated correctly."""
    res = determine_deviation([price_1, price_2])
    assert res == deviation


deviation_test_feeds = [
    FeedSpec(
        pair="ADA-BTC",
        label="ADA-BTC",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-DJED",
        label="ADA-DJED",
        interval=3600,
        deviation=2,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-IUSD",
        label="ADA-IUSD",
        interval=3600,
        deviation=5,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-USD",
        label="ADA-USD",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-USDM",
        label="ADA-USDM",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="AGIX-ADA",
        label="AGIX-ADA",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
]

deviation_test_feeds = [
    FeedSpec(
        pair="ADA-BTC",
        label="ADA-BTC",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-DJED",
        label="ADA-DJED",
        interval=3600,
        deviation=2,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-IUSD",
        label="ADA-IUSD",
        interval=3600,
        deviation=5,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-USD",
        label="ADA-USD",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="ADA-USDM",
        label="ADA-USDM",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
    FeedSpec(
        pair="AGIX-ADA",
        label="AGIX-ADA",
        interval=3600,
        deviation=1,
        source="",
        calculation="",
        status="",
        type="",
    ),
]


price_monitor_data_1 = {
    # Test live values at time of writing.
    "error": None,
    "data": [
        {"ADA-BTC": []},
        {"ADA-DJED": [0.7480787676, 0.747517805]},
        {"ADA-IUSD": [0.7360390497, 0.7395969064]},
        {"ADA-USD": [0.7440515, 0.74322]},
        {"ADA-USDM": [0.7375885532, 0.7482674595]},
        {"AGIX-ADA": []},
    ],
}

price_monitor_data_2 = {
    # Test values more-than.
    "error": None,
    "data": [
        {"ADA-BTC": [1, 1.01]},
        {"ADA-DJED": [1, 1.02]},
        {"ADA-IUSD": [1, 1.05]},
        {"ADA-USD": []},
        {"ADA-USDM": []},
        {"AGIX-ADA": []},
    ],
}

price_monitor_data_3 = {
    # Test values less-than.
    "error": None,
    "data": [
        {"ADA-BTC": [1, 1.001]},
        {"ADA-DJED": [1, 1.002]},
        {"ADA-IUSD": [1, 0.95]},
        {"ADA-USD": [1, 1]},
        {"ADA-USDM": [10, 9]},
        {"AGIX-ADA": [5, 4.95]},
    ],
}

expected_1 = {"feeds": ["ADA-USDM"]}
expected_2 = {"feeds": ["ADA-BTC", "ADA-DJED", "ADA-IUSD"]}
expected_3 = {"feeds": ["ADA-IUSD", "ADA-USDM", "AGIX-ADA"]}

compare_tests = [
    (price_monitor_data_1, expected_1),
    (price_monitor_data_2, expected_2),
    (price_monitor_data_3, expected_3),
]


@pytest.mark.parametrize("websocket_data, expected", compare_tests)
@pytest.mark.asyncio
async def test_compare_validator_data_deviations(websocket_data, expected):
    """Make sure that deviation data can be used to return pairs that
    need requesting.
    """
    res = await compare_validator_data_deviations(deviation_test_feeds, websocket_data)
    assert res == expected


kupo_1 = [
    ["CER/ADA-USD/3", 1754491804482, [1459789, 2000000]],  # latest data-point.
    ["CER/ADA-USD/3", 1054488922998, [145617, 200000]],
    ["CER/ADA-USD/3", 1004486104368, [72450253, 100000000]],
    ["CER/ADA-DJED/3", 1054482504002, [7286147931, 10000000000]],
    ["CER/ADA-DJED/3", 1754482504002, [1459750, 2000000]],  # latest data-point.
    ["CER/ADA-DJED/3", 1004482504002, [7286147931, 10000000000]],
    ["CER/ADA-iUSD/3", 1054482503950, [1822399613, 2500000000]],
    ["CER/ADA-iUSD/3", 1004482503950, [1822399613, 2500000000]],
    ["CER/ADA-iUSD/3", 1754482503950, [1459710, 2000000]],  # latest data-point.
]

collected = {
    "ADA-DJED": 0.7405390751,
    "ADA-IUSD": 0.7320001028,
    "ADA-USD": 0.73433129,
}

res_1 = [
    {"ADA-USD": [0.7298945, 0.73433129]},
    {"ADA-DJED": [0.729875, 0.7405390751]},
    {"ADA-IUSD": [0.729855, 0.7320001028]},
]


kupo_collate_tests = [({}, {}, []), (kupo_1, collected, res_1)]


@pytest.mark.parametrize("on_chain, latest_available, expected", kupo_collate_tests)
@pytest.mark.asyncio
async def test_collate_kupo_data(on_chain, latest_available, expected):
    """Provide some integration testing for kupo as an external service.
    These tests ensure that we order kupo data correctly and that the
    comparison data is returned correctly.
    """
    res = await collate_kupo_data(on_chain, latest_available)
    assert res == expected
