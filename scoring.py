"""Cleaning, the custom `cal` score and the join, moved out of bests.ipynb so they can be tested.

The formula is the one from the original notebook, unchanged (see the comments on each term).
"""
import numpy as np
import pandas as pd

NUMERIC_COLUMNS = ('place', 'vote', 'rate')


def clean_numbers(df):
    """Strip thousands separators and trailing dots, convert to numbers, drop rows that fail."""
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col].str.replace(',', '').str.rstrip('.'), errors='coerce')
    return df.dropna(subset=list(NUMERIC_COLUMNS)).reset_index(drop=True)


def dataset_stats(df):
    """Mean votes, mean rating, mean place, max place, max votes of the whole table."""
    return (df['vote'].mean(), df['rate'].mean(), df['place'].mean(),
            df['place'].max(), df['vote'].max())


def cal_score(v, p, r, vm, rm, pm, pM, vM):
    """Custom score: v = votes, p = place (1 = most popular), r = rating; the rest are dataset_stats."""
    vp = v + (pM - p)  # "evidence": votes plus how far the title is from the bottom of the popularity list
    return (vp / (vp + vm + pm) * r + (vm + pm) / (vp + vm + pm) * rm                        # term 1
            + r / (r + rm) * (vp / (pM + vM) * 10) + rm / (r + rm) * ((vm + pm) / (vM + pM) * 10)  # term 2
            + v / (v + vm) * ((pM - p) / pM * 10) + vm / (v + vm) * (pm / pM * 10)           # term 3
            + (pM - p) / ((pM - p) + pm) * (v / vM * 10) + pm / ((pM - p) + pm) * (v / vM * 10))  # term 4


def add_cal(df):
    """Return a copy of df with a `cal` column, using statistics computed from df itself."""
    vm, rm, pm, pM, vM = dataset_stats(df)
    out = df.copy()
    out['cal'] = cal_score(df['vote'], df['place'], df['rate'], vm, rm, pm, pM, vM)
    return out


def join_unambiguous(alldata, series, key='title'):
    """Inner join on `key`, first dropping keys that occur more than once on either side."""
    a = alldata[~alldata[key].duplicated(keep=False)]
    s = series[~series[key].duplicated(keep=False)]
    return pd.merge(a, s, how='inner', on=key, suffixes=('_x', '_y')).sort_values(by='cal', ascending=False)
