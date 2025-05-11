import scrapy

class imdbshowsSpider(scrapy.Spider):
    #identity

    name = 'imdbshowsSpider'

    #request
    def start_requests(self):
        url = 'https://www.imdb.com/search/title/?release_date=2022-01-01,2022-12-31&num_votes=1,&genres=Animation&title_type=tv_series,mini_series&count=250&ref_=adv_prv'
        # url = 'https://www.imdb.com/search/title/?num_votes=1,&count=250&ref_=adv_prv'
        yield  scrapy.Request(url=url, callback=self.parse)
        # return super().start_requests()

    #response
    def parse(self, response, **kwargs):
        for show in response.selector.xpath("//div[@class='lister-item-content']"):
            yield {
                'place': show.xpath(".//h3/span[1]/text()").extract_first(),
                'title': show.xpath(".//h3/a/text()").extract_first(),
                'rate': show.xpath(".//div/div[1]/strong/text()").extract_first(),
                'vote': show.xpath(".//p[4]/span[2]/text()").extract_first(),
                
                # 'show': show,
            }
        next_page = response.selector.xpath("//a[@class='lister-page-next next-page']/@href").extract_first()
        if next_page is not None:
            next_page_link = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_link, callback=self.parse)
        
        # return super().parse(response, **kwargs)c