import scrapy


class imdbshowsSpider(scrapy.Spider):
    #identity

    name = 'imdbshowsSpider'

    #request
    async def start(self):
        # Scrapy >= 2.13 calls start(); the old start_requests() is no longer used.
        url = 'https://www.imdb.com/search/title/?release_date=2022-01-01,2022-12-31&num_votes=1,&genres=Animation&title_type=tv_series,mini_series&count=250&ref_=adv_prv'
        # url = 'https://www.imdb.com/search/title/?num_votes=1,&count=250&ref_=adv_prv'
        yield scrapy.Request(url=url, callback=self.parse)

    #response
    def parse(self, response, **kwargs):
        # Selectors target IMDb's current (2023+) search layout. NOT verified against
        # the live site (see README); the old 2022 "lister-item-content" layout is gone.
        for show in response.css("li.ipc-metadata-list-summary-item"):
            href = show.css("a.ipc-title-link-wrapper::attr(href)").get() or ''
            # "1. Title" -> place "1.", title "Title"
            heading = show.css("h3.ipc-title__text::text").get() or ''
            place, _, title = heading.partition(' ')
            yield {
                'imdb_id': href.split('/')[2] if href.startswith('/title/') else None,
                'place': place or None,
                'title': title or None,
                'rate': show.css("span.ipc-rating-star--rating::text").get(),
                # text is like "(20K)" in the new layout; kept raw
                'vote': (show.css("span.ipc-rating-star--voteCount::text").getall() or [None])[-1],
            }
        # The new layout loads further pages with a JavaScript "50 more" button, so
        # there is no plain "next" link to follow; keep the old link as a fallback.
        next_page = response.css("a.lister-page-next::attr(href)").get()
        if next_page is not None:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
