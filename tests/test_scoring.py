import os

import pandas as pd
import pytest

from scoring import add_cal, cal_score, clean_numbers, dataset_stats, join_unambiguous

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

# Constants of the full 1.27M-row scrape, which is not in the repo. They were recovered by fitting the formula to the
# 395 rows of the committed out.csv (the fit reproduces every cal to 1e-11), not read from the data.
FULL = dict(vm=1039.81846376, rm=6.960127863216592, pm=633300.07999469, pM=1267220, vM=2678205)


def read(name):
    return pd.read_csv(os.path.join(FIXTURES, name), dtype=str)


def test_cal_reproduces_committed_out_csv_rows():
    """Six rows copied from out.csv: the formula must give the cal the original notebook saved."""
    rows = pd.read_csv(os.path.join(FIXTURES, 'out_rows.csv'))
    got = cal_score(rows['vote'], rows['place'], rows['rate'], **FULL)
    assert got.tolist() == pytest.approx(rows['cal'].tolist(), abs=1e-6)


def test_few_votes_cannot_beat_a_well_voted_show_at_the_same_place():
    """The point of the weighted rating: 9 votes at 9.5 must not outrank 20,000 votes at 8.5."""
    assert cal_score(9, 300000, 9.5, **FULL) < cal_score(20000, 300000, 8.5, **FULL)


def test_score_rises_with_rating_votes_and_popularity():
    base = cal_score(5000, 20000, 7.5, **FULL)
    assert cal_score(5000, 20000, 8.5, **FULL) > base       # higher rating
    assert cal_score(50000, 20000, 7.5, **FULL) > base      # more votes
    assert cal_score(5000, 2000, 7.5, **FULL) > base        # better (smaller) place


def test_clean_numbers_strips_commas_and_dots_and_drops_bad_rows():
    out = clean_numbers(read('alldata_small.csv'))
    assert out['title'].tolist() == ['Alpha', 'Beta', 'Gamma', 'Same Name', 'Same Name']  # 'Broken' (rate 'x') dropped
    assert out.loc[0, 'vote'] == 1000 and out.loc[0, 'place'] == 1


def test_add_cal_uses_statistics_of_its_own_table():
    out = add_cal(clean_numbers(read('alldata_small.csv')))
    vm, rm, pm, pM, vM = dataset_stats(out.drop(columns='cal'))
    first = out.iloc[0]
    assert first['cal'] == pytest.approx(cal_score(first['vote'], first['place'], first['rate'], vm, rm, pm, pM, vM))


def test_join_drops_titles_that_occur_twice_and_unmatched_titles():
    alldata = add_cal(clean_numbers(read('alldata_small.csv')))
    series = clean_numbers(read('series_small.csv'))
    joined = join_unambiguous(alldata, series)
    assert joined['title'].tolist() == ['Alpha']  # 'Same Name' is ambiguous in alldata, 'Only In Series' has no match
    assert {'place_x', 'place_y', 'rate_x', 'rate_y', 'cal'} <= set(joined.columns)
