"""Pubwatch tests."""

# pylint: disable=R0913

from typing import Final

import freezegun
import pytest

from src.pubwatch.compare import (
    collate_latest_timestamps,
    compare_direct_intervals,
    compare_intervals,
    get_delta,
    hour_delta_threshold,
    make_feed_interval_obj,
)
from src.pubwatch.objects import FeedInterval, feed_list, feed_list_expiring
from src.pubwatch.pubwatch import compare_gaps_by_label, remove_known_from_feed_list

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
    collated_timestamps = collate_latest_timestamps(ON_CHAIN_DATA)
    assert collated_timestamps == {
        "CER/ADA-DJED": 1723194014,
        "CER/IBTC-ADA": 1723194003,
        "CER/IETH-ADA": 1723194003,
        "CER/MIN-ADA": 1723194003,
        "CER/SNEK-ADA": 1723194003,
        "CER/SHEN-ADA": 1723194003,
        "CER/ADA-EUR": 1723194003,
        "CER/FACT-ADA": 1723194003,
        "CER/LQ-ADA": 1723194003,
        "CER/WMT-ADA": 1723194003,
        "CER/LENFI-ADA": 1723194003,
        "CER/NEWM-ADA": 1723194003,
        "CER/ADA-IUSD": 1723194003,
        "CER/ADA-USDM": 1723194003,
        "CER/HUNT-ADA": 1723194003,
        "CER/ADA-USD": 1723194002,
    }, "dict should contain latest timestamps from on-chain only"
    res = await compare_direct_intervals(
        latest_feed_timestamps=collated_timestamps,
        intervals=INTERVALS,
        threshold=0,
    )
    assert len(res) == len(INTERVALS)
    res = feed_list(res)
    for item in ["ADA-IUSD", "SHEN-ADA", "IBTC-ADA"]:
        assert item in res


@pytest.mark.asyncio
@freezegun.freeze_time("1971-08-09 09:11:01")
async def test_compare_and_return_all():
    """Provide more integration testing to test global functionality.

    Freezetime is set further in the past and so all feeds should be
    required.
    """
    collated_timestamps = collate_latest_timestamps(ON_CHAIN_DATA)
    res = await compare_direct_intervals(
        latest_feed_timestamps=collated_timestamps,
        intervals=INTERVALS,
        threshold=0,
    )
    assert len(res) == len(INTERVALS)
    res = feed_list(res)
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


ON_CHAIN_DATA_FOR_BATCHING: Final[list] = [
    ["CER/ADA-DJED/5", 1734171010000, [5183, 200000]],
    ["CER/MIN-ADA/5", 1734171010000, [108147, 50000]],
    ["CER/FACT-ADA/5", 1734171010000, [294703, 500000]],
    ["CER/LQ-ADA/5", 1734171010000, [1702987, 1000000]],
    ["CER/SNEK-ADA/5", 1734171010000, [1313, 200000]],
    ["CER/LENFI-ADA/5", 1734171010000, [346269, 1000000]],
    # 09:25.
    ["CER/HUNT-ADA/5", 1734168300000, [305979, 1000000]],
    # 09:20.
    ["CER/ADA-USD/5", 1734168010000, [70427, 200000]],
    # 09:10.
    ["CER/ADA-USDM/5", 1734167410000, [102779, 250000]],
]


@pytest.mark.asyncio
@freezegun.freeze_time("2024-12-14 10:10:10")
async def test_compare_intervals_with_batching():
    """Provide some integration testing for when batching is enabled.
    Batching should increase the number of feeds we're requesting by
    finding a bigger threshold of those about to go stale.
    """
    collated_timestamps = collate_latest_timestamps(ON_CHAIN_DATA_FOR_BATCHING)
    assert collated_timestamps == {
        "CER/ADA-DJED": 1734171010,
        "CER/MIN-ADA": 1734171010,
        "CER/SNEK-ADA": 1734171010,
        "CER/FACT-ADA": 1734171010,
        "CER/LQ-ADA": 1734171010,
        "CER/LENFI-ADA": 1734171010,
        # 09:25
        "CER/HUNT-ADA": 1734168300,
        # 09:20.
        "CER/ADA-USD": 1734168010,
        # 09;10.
        "CER/ADA-USDM": 1734167410,
    }, "dict should contain latest timestamps from on-chain only"

    # Test 1: Using the feed list with no batching, return a single
    # result that has expired by one hour.
    res = await compare_intervals(
        intervals=INTERVALS,
        comparison_data=ON_CHAIN_DATA_FOR_BATCHING,
        threshold=0,
        hour_boundary=False,
        batching=False,
        batch_time=0,
    )
    assert res == ["ADA-USDM"]
    # Test 2: extend the range of batching to fifteen minutes, i.e. the
    # feed will expire within 15 mins, so we need to post.
    res = await compare_intervals(
        intervals=INTERVALS,
        comparison_data=ON_CHAIN_DATA_FOR_BATCHING,
        threshold=0,
        hour_boundary=False,
        batching=True,
        batch_time=900,
    )
    assert len(res) == 3
    for item in ["ADA-USDM", "ADA-USD", "HUNT-ADA"]:
        assert item in res


HOURLY_EXAMPLES: Final[str] = [
    # 04:01, 04:00, publish (1 hour interval + 120s threshold)
    (1723608060, 1723608000, 3600, 120, False),
    # 04:02, 04:01, publish (1 hour interval + 120s threshold)
    (1723608120, 1723608060, 3600, 120, False),
    # 04:10, 03:45, publish (1 hour interval + 120s threshold)
    (1723608652, 1723607100, 3600, 120, True),
    # 08:01, 07:01, publish (1 hour interval + 120s threshold)
    (1723622460, 1723618860, 3600, 120, True),
    # 08:01, 07:01, no publish (2 hour interval + 120s threshold)
    (1723622460, 1723618860, 7200, 120, False),
    # 08:01, 06:10, publish (2 hour interval + 120s threshold)
    (1723622460, 1723615852, 7200, 120, True),
    # 08v01, 07:01, no publish (2 hour interval + 120s threshold)
    (1723622460, 1723618860, 7200, 120, False),
    # 08:01, 06:01, publish (2 hour interval + 120s threshold)
    (1723622460, 1723615260, 7200, 120, True),
    # 10:44, 09:58, no publish (63 minute interval (3800s) + 120s threshold)
    (1723632286, 1723629480, 3800, 120, False),
    # 10:44, 09:57, publish (1 hour interval + 120s threshold)
    (1723632286, 1723629420, 3600, 120, True),
    # 10:44, 09:57, publish (1 hour interval + 320s threshold)
    (1723632286, 1723629420, 3600, 320, True),
    # 10:44, 10:04, no publish (1 hour interval + 320s threshold)
    (1723632286, 1723629851, 3600, 0, False),
    # 10:44, 07:17, no publish (1 hour interval + 0s threshold)
    (1723632286, 1723619851, 3600, 0, True),
    # 10:44, 07:17, no publish (4 hour interval + 0s threshold)
    (1723632286, 1723619851, 14400, 0, False),
]


@pytest.mark.parametrize(
    "now, latest_timestamp, interval, threshold, publish", HOURLY_EXAMPLES
)
def test_hour_delta_threshold(
    mocker, now, latest_timestamp, interval, threshold, publish
):
    """Test that our code works when using an hourly baseline for
    publication. An hourly baseline means that we try to publish on the
    hour, and so will publish even if the interval is slightly higher
    than the current time.
    """
    mocker.patch("time.time", return_value=now)
    hour_delta = hour_delta_threshold(
        latest_timestamp=latest_timestamp, interval=interval, threshold=threshold
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
async def test_compare_gaps_by_label(feeds, on_chain, expected):
    """Ensure that the compare gaps function works as expected and
    only returns gaps based on what is requested versus what is
    on-chain.
    """
    res = await compare_gaps_by_label(feeds=feeds, on_chain_data=on_chain)
    assert isinstance(res, list)
    assert len(res) == len(expected)
    for item in res:
        assert item in expected


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
    res = await remove_known_from_feed_list(label_based_gaps=gaps, on_chain=on_chain)
    assert isinstance(res, list)
    assert len(res) == len(expected)
    for item in res:
        assert item in expected


def test_objects_expiry():
    """Perform some basic tests around objects."""
    fi1 = FeedInterval(
        feed_name="ada-usd",
        time_left=100,
        interval=100,
        required=False,
    )
    assert fi1.feed_name == "ada-usd"
    assert feed_list_expiring([fi1], 0) == []
    assert feed_list_expiring([fi1], 101) == ["ada-usd"]
    fi1.time_left = 1
    fi1.interval = 100
    assert feed_list_expiring([fi1], 0) == []
    assert feed_list_expiring([fi1], 1) == ["ada-usd"]
    fi1.time_left = 5000
    fi1.interval = 3600
    assert feed_list_expiring([fi1], 0) == []
    assert feed_list_expiring([fi1], 600) == []
    assert feed_list_expiring([fi1], 6001) == ["ada-usd"]


def test_interval_obj():
    """Provide some tests for the creation of our interval object."""
    obj1 = make_feed_interval_obj(
        curr_time=2600,
        on_chain_timestamp=3000,
        threshold=10,
        interval=3600,
    )
    assert obj1.elapsed == 400
    assert obj1.feed_name == "UNTITLED"
    assert obj1.total_time_elapsed == 410
    assert obj1.interval == 3600
    assert obj1.time_left == 3190
    assert obj1.required is False

    obj2 = make_feed_interval_obj(
        curr_time=10000,
        on_chain_timestamp=13600,
        threshold=0,
        interval=3600,
    )
    assert obj2.elapsed == 3600
    assert obj2.feed_name == "UNTITLED"
    assert obj2.total_time_elapsed == 3600
    assert obj2.interval == 3600
    assert obj2.time_left == 0
    assert obj2.required is False


def test_get_delta():
    """Ensure get_delta is returning sensible information."""
    current = 2600
    on_chain = 1000
    res = get_delta(current, on_chain)
    # time elapsed is 1600 seconds.
    assert res == 1600
