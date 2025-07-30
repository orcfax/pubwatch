"""Test basic price montioring functions."""

import pytest

from src.pubwatch.feed_helper import FeedSpec
from src.pubwatch.price_monitor import (
    compare_validator_data_websocket,
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
async def test_compare_validator_data_websocket(websocket_data, expected):
    """Make sure that deviation data can be used to return pairs that
    need requesting.
    """
    res = await compare_validator_data_websocket(deviation_test_feeds, websocket_data)
    assert res == expected
