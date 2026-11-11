import pytest
from marathon_registration import entry_fee, start_wave, finisher_status


@pytest.mark.parametrize("race, age, message", [
    ("ultra", 30, "unknown race"),
    ("5k", 11, "too young"),
    ("half", 17, "too young for this distance"),
])
def test_entry_fee_rejections(race, age, message):
    with pytest.raises(ValueError, match=message):
        entry_fee(race, age, False, False)


def test_entry_fee_discounts_and_tshirt():
    # 1800 - 25% = 1350; senior discount gives 675; T-shirt adds 300.
    assert entry_fee("full", 65, True, True) == 975


@pytest.mark.parametrize("time, race, expected", [
    (None, "full", "D"),
    (180, "full", "A"),
    (240, "full", "B"),
    (241, "full", "C"),
    (90, "5k", "A"),
])
def test_waves(time, race, expected):
    assert start_wave(time, race) == expected


@pytest.mark.parametrize("time, race, missed, expected", [
    (100, "5k", 1, "DSQ"),
    (360, "full", 0, "finisher"),
    (180, "half", 0, "finisher"),
    (91, "5k", 0, "DNF"),
])
def test_status(time, race, missed, expected):
    assert finisher_status(time, race, missed) == expected
@pytest.mark.parametrize("race, age, early, shirt, expected", [
    ("10k", 30, False, False, 800),
    ("5k", 12, False, False, 500),
    ("5k", 64, False, False, 500),
    ("5k", 65, False, False, 250),
    ("half", 18, False, False, 1200),
    ("full", 18, False, False, 1800),
])
def test_fee_boundaries(race, age, early, shirt, expected):
    assert entry_fee(race, age, early, shirt) == expected


@pytest.mark.parametrize("time, race, expected", [
    (90, "5k", "A"),
    (91, "5k", "B"),
    (120, "5k", "B"),
    (121, "5k", "C"),
    (180, "full", "A"),
    (181, "full", "B"),
    (240, "full", "B"),
    (241, "full", "C"),
])
def test_wave_boundaries(time, race, expected):
    assert start_wave(time, race) == expected


@pytest.mark.parametrize("time, race, missed, expected", [
    (90, "5k", 0, "finisher"),
    (91, "5k", 0, "DNF"),
    (180, "half", 0, "finisher"),
    (181, "half", 0, "DNF"),
    (360, "full", 0, "finisher"),
    (361, "full", 0, "DNF"),
    (1, "full", 1, "DSQ"),
])
def test_status_boundaries(time, race, missed, expected):
    assert finisher_status(time, race, missed) == expected
