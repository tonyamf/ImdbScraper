import os

import pytest
from scrapy.http import HtmlResponse

from imdb2v.spiders.imdbshows import imdbshowsSpider
from scoring import clean_numbers

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'imdb_sample.html')


def parse_fixture():
    with open(FIXTURE, 'rb') as f:
        body = f.read()
    response = HtmlResponse(url='https://www.imdb.com/search/title/', body=body, encoding='utf-8')
    return list(imdbshowsSpider().parse(response))


def test_parse_extracts_id_place_title_rating_and_votes():
    """The fixture is hand-written to match the selectors, NOT a saved IMDb page: this tests the parsing logic only."""
    items = parse_fixture()
    assert items == [{'imdb_id': 'tt0000001', 'place': '1.', 'title': 'Example Show', 'rate': '8.7', 'vote': '(20K)'}]


def test_start_makes_one_request_for_2022_animated_series():
    import asyncio

    async def first():
        return [r async for r in imdbshowsSpider().start()]

    requests = asyncio.run(first())
    assert len(requests) == 1
    assert 'release_date=2022-01-01,2022-12-31' in requests[0].url and 'genres=Animation' in requests[0].url


@pytest.mark.xfail(reason="Real bug: the spider keeps votes as '(20K)' and clean_numbers turns that into NaN, so every "
                          "row of a fresh crawl would be dropped by the notebook (see 2_fix/review.md in HubRefine).",
                   strict=True)
def test_spider_output_survives_the_notebook_cleaning():
    import pandas as pd
    df = pd.DataFrame(parse_fixture()).astype(str)
    assert len(clean_numbers(df)) == 1
