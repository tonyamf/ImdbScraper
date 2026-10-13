1. Web Scraping with Scrapy
Purpose: Extract animation TV series/mini-series data from IMDb released in 2022.

Key Components:
Spider Name: imdbshowsSpider

Target URL: Filters 2022 releases with animation genre, TV series/mini-series type, and minimum 1 vote.

Data Extracted:

Ranking position (place)

Title (title)

IMDb rating (rate)

Number of votes (vote)

Pagination Handling: Follows "Next" page links recursively.

Code Flow:
Starts at the initial URL.

Parses the HTML response using XPath selectors.

Yields extracted data as dictionaries.

Checks for a "Next Page" link and repeats the process.

2. Data Processing & Analysis
Purpose: Calculate a custom weighted score (cal) to rank shows.

Key Steps:
Data Loading:

data.csv: Raw scraped data (about 1.27 million rows; not included in this repo).

series22.csv: Additional reference data (assumed to have matching titles).

Data Cleaning:

Remove commas from vote columns.

Convert vote and place to numeric types.

Statistical Metrics:

Compute means (vm, rm, pm) and max values (pM, vM) for votes, ratings, and rankings.

Custom Score Calculation:

A complex formula combining:

Weighted average of rating and vote count.

Normalization by max/mean values.

Multiple additive terms balancing popularity and ranking position.

Example term:

python
(row['vote'] / (row['vote'] + vm)) * ((pM - row['place']) / pM * 10)

3. Data Merging & Output
Purpose: Generate a ranked list of shows based on the custom score.

Workflow:
Merge Datasets:

Inner join alldata and series on title (on `imdb_id` if both files have it). Titles occurring more than once on either side are dropped as ambiguous.

Sorting:

Order by cal (descending) to prioritize top-rated shows.

Output:

Save results to out.csv.

## How to run

Tested with Python 3.11 (see `requirements.txt` for pinned versions).

```bash
python -m venv /tmp/venv && . /tmp/venv/bin/activate
pip install -r requirements.txt

# 1. Spider (writes data.csv-style rows; one request per page, obeys robots.txt)
scrapy crawl imdbshowsSpider -O scraped.json

# 2. Notebook, headless (or open bests.ipynb in Jupyter)
jupyter nbconvert --to notebook --execute bests.ipynb --output executed.ipynb
```

**What works and what does not**

- The notebook runs top to bottom. `data.csv` (the full scrape) is not in the repo, so without it the notebook uses `data_sample.csv`: 393 rows recovered from the `*_x` columns of the committed `out.csv`. With the sample the means/maxima used by `cal` differ from the full data, so the scores in `out_sample.csv` are **not** comparable to those in `out.csv`. `out.csv` is the original result from the full data and is kept unchanged.
- The spider starts correctly on Scrapy 2.19 but its CSS selectors target IMDb's current layout and are **untested against the live site** (the sandbox where this was fixed could not reach imdb.com). The old 2022 XPath selectors no longer match the site. Current IMDb search pages load more results with a JavaScript button, so only the first page is collected. The spider now also emits `imdb_id`, but `series22.csv` has no id column, so the committed data is still joined on title.
- Proof of the last run: `proof/run_output.txt`.

## Known issues (not fixed)

- The `cal` formula is long and hard to read (now vectorized, same formula, original behaviour).
- Joining on title can mismatch different shows with the same name; ambiguous titles are dropped.
- Title/vote scraping from IMDb needs re-validation against the live site.

