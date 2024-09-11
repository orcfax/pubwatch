"""Pubwatch tests."""

from typing import Final

import freezegun
import pytest

from src.pubwatch.pubwatch import (
    collate_latest_timestamps,
    compare_gaps,
    compare_intervals,
    hour_baseline_delta,
    remove_gaps,
)

ON_CHAIN_EX: Final[list] = [
    ["CER/iBTC-ADA/3", 1723186803981, [79234635919, 500000]],
    ["CER/iETH-ADA/3", 1723186803981, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723186803981, [42663, 1000000]],
    ["CER/SNEK-ADA/3", 1723186803981, [591, 250000]],
    ["CER/SHEN-ADA/3", 1723186803981, [1025151, 1000000]],
    ["CER/ADA-EUR/3", 1723186803981, [3989, 12500]],
    ["CER/FACT-ADA/3", 1723186803981, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723186803981, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723186803981, [295473, 500000]],
    ["CER/LENFI-ADA/3", 1723186803981, [1710537, 1000000]],
    ["CER/NEWM-ADA/3", 1723186803981, [129, 20000]],
    ["CER/ADA-DJED/3", 1723186803981, [21647, 62500]],
    ["CER/ADA-iUSD/3", 1723186803981, [410779, 1000000]],
    ["CER/ADA-USDM/3", 1723186803981, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723186803981, [305973, 1000000]],
    ["CER/ADA-USD/3", 1723186803981, [697, 2000]],
    ["CER/iBTC-ADA/3", 1723183204018, [9913737553, 62500]],
    ["CER/iETH-ADA/3", 1723183204006, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723183203988, [42663, 1000000]],
    ["CER/SNEK-ADA/3", 1723183203976, [47, 20000]],
    ["CER/SHEN-ADA/3", 1723183204006, [1025151, 1000000]],
    ["CER/ADA-EUR/3", 1723183203980, [159523, 500000]],
    ["CER/FACT-ADA/3", 1723183203958, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723183203944, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723183203935, [29519, 50000]],
    ["CER/LENFI-ADA/3", 1723183203913, [850833, 500000]],
    ["CER/NEWM-ADA/3", 1723183203896, [6449, 1000000]],
    ["CER/ADA-DJED/3", 1723183203891, [21647, 62500]],
    ["CER/ADA-iUSD/3", 1723183203927, [25629, 62500]],
    ["CER/ADA-USDM/3", 1723183203877, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723183203898, [305973, 1000000]],
    ["CER/ADA-USD/3", 1723183203849, [871, 2500]],
    ["CER/iBTC-ADA/3", 1723179603485, [9913737553, 62500]],
    ["CER/iETH-ADA/3", 1723179603464, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723179603451, [42643, 1000000]],
    ["CER/SNEK-ADA/3", 1723179603437, [2343, 1000000]],
    ["CER/SHEN-ADA/3", 1723179603402, [102557, 100000]],
    ["CER/ADA-EUR/3", 1723179603372, [317297, 1000000]],
    ["CER/FACT-ADA/3", 1723179603350, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723179603328, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723179603276, [294989, 500000]],
    ["CER/LENFI-ADA/3", 1723179603538, [340759, 200000]],
    ["CER/NEWM-ADA/3", 1723179603250, [6449, 1000000]],
    ["CER/ADA-DJED/3", 1723179603529, [173497, 500000]],
    ["CER/ADA-iUSD/3", 1723179603166, [410443, 1000000]],
    ["CER/ADA-USDM/3", 1723179603403, [172353, 500000]],
    ["CER/HUNT-ADA/3", 1723179603108, [152993, 500000]],
    ["CER/ADA-USD/3", 1723179603040, [1729, 5000]],
    ["CER/ADA-USD/3", 1723178541176, [17427, 50000]],
    ["CER/ADA-DJED/3", 1723176183087, [350251, 1000000]],
    ["CER/iBTC-ADA/3", 1723176003320, [9913737553, 62500]],
    ["CER/iETH-ADA/3", 1723176003312, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723176003304, [5349, 125000]],
    ["CER/SNEK-ADA/3", 1723176003288, [1159, 500000]],
    ["CER/SHEN-ADA/3", 1723176003270, [102557, 100000]],
    ["CER/ADA-EUR/3", 1723176003254, [322393, 1000000]],
    ["CER/FACT-ADA/3", 1723176003236, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723176003222, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723176003210, [294703, 500000]],
    ["CER/LENFI-ADA/3", 1723176003189, [1702987, 1000000]],
    ["CER/NEWM-ADA/3", 1723176003169, [1313, 200000]],
    ["CER/ADA-iUSD/3", 1723176003276, [102669, 250000]],
    ["CER/ADA-USDM/3", 1723176003283, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723176003146, [305979, 1000000]],
    ["CER/ADA-USD/3", 1723176003159, [70427, 200000]],
    ["CER/ADA-iUSD/3", 1723173062939, [102779, 250000]],
]


def test_compare():
    """Ensure a basic comparison function is predictable."""
    expected_max_ts = 1723186803
    res = collate_latest_timestamps(ON_CHAIN_EX)
    assert res == {
        "CER/IBTC-ADA": 1723186803,
        "CER/IETH-ADA": 1723186803,
        "CER/MIN-ADA": 1723186803,
        "CER/SNEK-ADA": 1723186803,
        "CER/SHEN-ADA": 1723186803,
        "CER/ADA-EUR": 1723186803,
        "CER/FACT-ADA": 1723186803,
        "CER/LQ-ADA": 1723186803,
        "CER/WMT-ADA": 1723186803,
        "CER/LENFI-ADA": 1723186803,
        "CER/NEWM-ADA": 1723186803,
        "CER/ADA-DJED": 1723186803,
        "CER/ADA-IUSD": 1723186803,
        "CER/ADA-USDM": 1723186803,
        "CER/HUNT-ADA": 1723186803,
        "CER/ADA-USD": 1723186803,
    }
    for value in res.values():
        assert value == expected_max_ts


INTERVALS: Final[dict] = {
    "CER/ADA-IUSD": 1,
    "CER/ADA-USDM": 3480,
    "CER/ADA-DJED": 3480,
    "CER/SHEN-ADA": 2,
    "CER/MIN-ADA": 3480,
    "CER/FACT-ADA": 3480,
    "CER/ADA-USD": 3480,
    "CER/LQ-ADA": 3480,
    "CER/SNEK-ADA": 3480,
    "CER/LENFI-ADA": 3480,
    "CER/HUNT-ADA": 3480,
    "CER/IBTC-ADA": 657,
    "CER/IETH-ADA": 3480,
}
ON_CHAIN_DATA: Final[list] = [
    ["CER/ADA-DJED/3", 1723194014750, [345233, 1000000]],
    ["CER/iBTC-ADA/3", 1723194003299, [157397269397, 1000000]],
    ["CER/iETH-ADA/3", 1723194003307, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723194003260, [42663, 1000000]],
    ["CER/SNEK-ADA/3", 1723194003208, [1177, 500000]],
    ["CER/SHEN-ADA/3", 1723194003171, [256647, 250000]],
    ["CER/ADA-EUR/3", 1723194003160, [3183, 10000]],
    ["CER/FACT-ADA/3", 1723194003107, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723194003102, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723194003056, [296561, 500000]],
    ["CER/LENFI-ADA/3", 1723194003038, [860993, 500000]],
    ["CER/NEWM-ADA/3", 1723194003026, [129, 20000]],
    ["CER/ADA-iUSD/3", 1723194003208, [41147, 100000]],
    ["CER/ADA-USDM/3", 1723194003258, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723194003004, [38029, 125000]],
    ["CER/ADA-USD/3", 1723194002979, [86801, 250000]],
    ["CER/iBTC-ADA/3", 1723190404677, [79234635919, 500000]],
    ["CER/iETH-ADA/3", 1723190404705, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723190404689, [21391, 500000]],
    ["CER/SNEK-ADA/3", 1723190403523, [2351, 1000000]],
    ["CER/SHEN-ADA/3", 1723190403515, [1025151, 1000000]],
    ["CER/ADA-EUR/3", 1723190404692, [318449, 1000000]],
    ["CER/FACT-ADA/3", 1723190403496, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723190403467, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723190403496, [593227, 1000000]],
    ["CER/LENFI-ADA/3", 1723190403456, [1725647, 1000000]],
    ["CER/NEWM-ADA/3", 1723190403447, [129, 20000]],
    ["CER/ADA-DJED/3", 1723190403424, [21647, 62500]],
    ["CER/ADA-iUSD/3", 1723190403411, [8227, 20000]],
    ["CER/ADA-USDM/3", 1723190403406, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723190403429, [38029, 125000]],
    ["CER/ADA-USD/3", 1723190403402, [3477, 10000]],
    ["CER/iBTC-ADA/3", 1723186803981, [79234635919, 500000]],
    ["CER/iETH-ADA/3", 1723186803905, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723186803890, [42663, 1000000]],
    ["CER/SNEK-ADA/3", 1723186803859, [591, 250000]],
    ["CER/SHEN-ADA/3", 1723186803851, [1025151, 1000000]],
    ["CER/ADA-EUR/3", 1723186804195, [3989, 12500]],
    ["CER/FACT-ADA/3", 1723186803803, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723186803733, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723186803662, [295473, 500000]],
    ["CER/LENFI-ADA/3", 1723186803833, [1710537, 1000000]],
    ["CER/NEWM-ADA/3", 1723186803633, [129, 20000]],
    ["CER/ADA-DJED/3", 1723186803598, [21647, 62500]],
    ["CER/ADA-iUSD/3", 1723186803575, [410779, 1000000]],
    ["CER/ADA-USDM/3", 1723186803551, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723186803837, [305973, 1000000]],
    ["CER/ADA-USD/3", 1723186803519, [697, 2000]],
    ["CER/iBTC-ADA/3", 1723183204018, [9913737553, 62500]],
    ["CER/iETH-ADA/3", 1723183204006, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723183203988, [42663, 1000000]],
    ["CER/SNEK-ADA/3", 1723183203976, [47, 20000]],
    ["CER/SHEN-ADA/3", 1723183204006, [1025151, 1000000]],
    ["CER/ADA-EUR/3", 1723183203980, [159523, 500000]],
    ["CER/FACT-ADA/3", 1723183203958, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723183203944, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723183203935, [29519, 50000]],
    ["CER/LENFI-ADA/3", 1723183203913, [850833, 500000]],
    ["CER/NEWM-ADA/3", 1723183203896, [6449, 1000000]],
    ["CER/ADA-DJED/3", 1723183203891, [21647, 62500]],
    ["CER/ADA-iUSD/3", 1723183203927, [25629, 62500]],
    ["CER/ADA-USDM/3", 1723183203877, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723183203898, [305973, 1000000]],
    ["CER/ADA-USD/3", 1723183203849, [871, 2500]],
    ["CER/iBTC-ADA/3", 1723179603485, [9913737553, 62500]],
    ["CER/iETH-ADA/3", 1723179603464, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723179603451, [42643, 1000000]],
    ["CER/SNEK-ADA/3", 1723179603437, [2343, 1000000]],
    ["CER/SHEN-ADA/3", 1723179603402, [102557, 100000]],
    ["CER/ADA-EUR/3", 1723179603372, [317297, 1000000]],
    ["CER/FACT-ADA/3", 1723179603350, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723179603328, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723179603276, [294989, 500000]],
    ["CER/LENFI-ADA/3", 1723179603538, [340759, 200000]],
    ["CER/NEWM-ADA/3", 1723179603250, [6449, 1000000]],
    ["CER/ADA-DJED/3", 1723179603529, [173497, 500000]],
    ["CER/ADA-iUSD/3", 1723179603166, [410443, 1000000]],
    ["CER/ADA-USDM/3", 1723179603403, [172353, 500000]],
    ["CER/HUNT-ADA/3", 1723179603108, [152993, 500000]],
    ["CER/ADA-USD/3", 1723179603040, [1729, 5000]],
    ["CER/ADA-USD/3", 1723178541176, [17427, 50000]],
    ["CER/ADA-DJED/3", 1723176183087, [350251, 1000000]],
    ["CER/iBTC-ADA/3", 1723176003320, [9913737553, 62500]],
    ["CER/iETH-ADA/3", 1723176003312, [3526254483, 500000]],
    ["CER/MIN-ADA/3", 1723176003304, [5349, 125000]],
    ["CER/SNEK-ADA/3", 1723176003288, [1159, 500000]],
    ["CER/SHEN-ADA/3", 1723176003270, [102557, 100000]],
    ["CER/ADA-EUR/3", 1723176003254, [322393, 1000000]],
    ["CER/FACT-ADA/3", 1723176003236, [5183, 200000]],
    ["CER/LQ-ADA/3", 1723176003222, [108147, 50000]],
    ["CER/WMT-ADA/3", 1723176003210, [294703, 500000]],
    ["CER/LENFI-ADA/3", 1723176003189, [1702987, 1000000]],
    ["CER/NEWM-ADA/3", 1723176003169, [1313, 200000]],
    ["CER/ADA-iUSD/3", 1723176003276, [102669, 250000]],
    ["CER/ADA-USDM/3", 1723176003283, [346269, 1000000]],
    ["CER/HUNT-ADA/3", 1723176003146, [305979, 1000000]],
    ["CER/ADA-USD/3", 1723176003159, [70427, 200000]],
    ["CER/ADA-iUSD/3", 1723173062939, [102779, 250000]],
]


@pytest.mark.asyncio
@freezegun.freeze_time("2024-08-09 09:11:01")
async def test_compare_and_return():
    """Provide more integration testing to test global functionality.

    Values in INTERVALS are set to 1 so that we guarantee a delta which
    requires a value to be returned.
    """
    res = await compare_intervals(INTERVALS, ON_CHAIN_DATA)
    for item in ["ADA-IUSD", "SHEN-ADA", "IBTC-ADA"]:
        assert item in res


@pytest.mark.asyncio
@freezegun.freeze_time("1971-08-09 09:11:01")
async def test_compare_and_return_all():
    """Provide more integration testing to test global functionality.

    Freezetime is set further in the past and so all feeds should be
    required.
    """
    res = await compare_intervals(INTERVALS, ON_CHAIN_DATA)
    assert len(set(res)) == len(INTERVALS.values())
    assert res == [
        "ADA-DJED",
        "IBTC-ADA",
        "IETH-ADA",
        "MIN-ADA",
        "SNEK-ADA",
        "SHEN-ADA",
        "FACT-ADA",
        "LQ-ADA",
        "LENFI-ADA",
        "ADA-IUSD",
        "ADA-USDM",
        "HUNT-ADA",
        "ADA-USD",
    ]


HOURLY_EXAMPLES: Final[str] = [
    # 0401, 0400, publish (1 hour interval + 120s threshold)
    (1723608060, 1723608000, 3600, 120, False),
    # 0402, 0401, publish (1 hour interval + 120s threshold)
    (1723608120, 1723608060, 3600, 120, False),
    # 0401, 0345, publish (1 hour interval + 120s threshold)
    (1723608060, 1723607100, 3600, 120, True),
    # 0801, 0701, publish (1 hour interval + 120s threshold)
    (1723622460, 1723618860, 3600, 120, True),
    # 0801, 0701, no publish (2 hour interval + 120s threshold)
    (1723622460, 1723618860, 7200, 120, False),
    # 0801, 0701, no publish (2 hour interval + 120s threshold)
    (1723622460, 1723615260, 7200, 120, True),
    # 1044, 0958, no publish (1 hour interval + 120s threshold)
    (1723632286, 1723629480, 3600, 120, False),
    # 1044, 09:57, no publish (1 hour interval + 120s threshold)
    (1723632286, 1723629420, 3600, 120, True),
    # 1044, 09:57, no publish (1 hour interval + 320s threshold)
    (1723632286, 1723629420, 3600, 320, False),
]


@pytest.mark.parametrize("now, latest, interval, threshold, publish", HOURLY_EXAMPLES)
def test_hour_baseline_interval(now, latest, interval, threshold, publish):
    """Test that our code works when using an hourly baseline for
    publication.
    """
    hour_delta = hour_baseline_delta(
        now=now, latest=latest, window=interval, threshold=threshold
    )
    assert hour_delta == publish


# Test data for anything that isn't on-chain but should be there and
# would otherwise not appear during interval comparison.

# All four cer-feeds appear in the on-chain data and so are not gaps
# on-chain.
INTERVALS_NONE: Final[dict] = {
    "CER/ADA-IUSD": 1,
    "CER/ADA-USDM": 1,
    "CER/ADA-DJED": 1,
    "CER/SHEN-ADA": 1,
}

ON_CHAIN_DATA_NONE: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194003299, [157397269397, 1000000]],
    ["CER/SHEN-ADA/3", 1723194003307, [3526254483, 500000]],
    ["CER/ADA-DJED/3", 1723194003307, [3526254483, 500000]],
]

# BTN-ADA does not appear in the on-chain data and so this is a
# legitimate gap that needs to be plugged.
INTERVALS_ONE: Final[dict] = {
    "CER/ADA-IUSD": 1,
    "CER/ADA-USDM": 1,
    "CER/ADA-DJED": 1,
    "CER/BTN-ADA": 1,
}

ON_CHAIN_DATA_ONE: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194003299, [157397269397, 1000000]],
    ["CER/ADA-DJED/3", 1723194003307, [3526254483, 500000]],
]

# FACT-ADA and BTN-ADA doe not appear in the on-chain data and so
# their intervals cannot be compared and so need to be published.
INTERVALS_TWO: Final[dict] = {
    "CER/ADA-IUSD": 1,
    "CER/ADA-USDM": 1,
    "CER/FACT-ADA": 1,
    "CER/BTN-ADA": 1,
}

ON_CHAIN_DATA_TWO: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194003299, [157397269397, 1000000]],
]

INTERVALS_NONE_MORE_ONCHAIN: Final[dict] = {
    "CER/ADA-IUSD": 1,
}

ON_CHAIN_DATA_NONE_MORE_ONCHAIN: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194003299, [157397269397, 1000000]],
    ["CER/SHEN-ADA/3", 1723194003307, [3526254483, 500000]],
    ["CER/ADA-DJED/3", 1723194003307, [3526254483, 500000]],
]

GAPS_TESTS = [
    (INTERVALS_NONE, ON_CHAIN_DATA_NONE, []),
    (INTERVALS_ONE, ON_CHAIN_DATA_ONE, ["BTN-ADA"]),
    (INTERVALS_TWO, ON_CHAIN_DATA_TWO, ["BTN-ADA", "FACT-ADA"]),
    (INTERVALS_NONE_MORE_ONCHAIN, ON_CHAIN_DATA_NONE_MORE_ONCHAIN, []),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("feeds, on_chain, expected", GAPS_TESTS)
async def test_compare_gaps(feeds, on_chain, expected):
    """Ensure that the compare gaps function works as expected and
    only returns gaps based on what is requested versus what is
    on-chain.
    """
    res = await compare_gaps(feeds=feeds, on_chain_data=on_chain)
    assert res == expected


# On-chain data we anticipate removing zero values from.
ON_CHAIN_DATA_NONE_REMOVED: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194014750, [345233, 1000000]],
    ["CER/SHEN-ADA/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-DJED/3", 1723194014750, [345233, 1000000]],
]

# On-chain data we anticipate removing one value from.
ON_CHAIN_DATA_ONE_REMOVED: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-DJED/3", 1723194014750, [345233, 1000000]],
]

# One value remove because it doesn't need comparison.
RES_ON_CHAIN_DATA_ONE_REMOVED: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-DJED/3", 1723194014750, [345233, 1000000]],
]

# On-chain data we anticipate removing two values from.
ON_CHAIN_DATA_TWO_REMOVED: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USDM/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-DJED/3", 1723194014750, [345233, 1000000]],
]

# Two values remove because it doesn't need comparison.
RES_ON_CHAIN_DATA_TWO_REMOVED: Final[list] = [
    ["CER/ADA-IUSD/3", 1723194014750, [345233, 1000000]],
    ["CER/ADA-USD/3", 1723194014750, [345233, 1000000]],
]

REMOVE_GAPS_TESTS = [
    ([], ON_CHAIN_DATA_NONE_REMOVED, ON_CHAIN_DATA_NONE_REMOVED),
    (["ADA-USD"], ON_CHAIN_DATA_ONE_REMOVED, RES_ON_CHAIN_DATA_ONE_REMOVED),
    (
        ["ADA-USDM", "ADA-DJED"],
        ON_CHAIN_DATA_TWO_REMOVED,
        RES_ON_CHAIN_DATA_TWO_REMOVED,
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("gaps, on_chain, expected", REMOVE_GAPS_TESTS)
async def test_remove_gaps(gaps, on_chain, expected):
    """Ensure that we can remove values from the on-chain results as
    needed.
    """
    res = await remove_gaps(gaps=gaps, on_chain=on_chain)
    assert res == expected
