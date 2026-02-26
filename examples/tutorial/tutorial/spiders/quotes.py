from typing import ClassVar

import scrapy

from tutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains: ClassVar[list[str]] = ["quotes.toscrape.com"]
    start_urls: ClassVar[list[str]] = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        for quote in response.css(".quote"):
            item = QuoteItem(
                quote=quote.css(".text::text").get(),
                author=quote.css(".author::text").get(),
                author_url=response.urljoin(quote.css(".author a::attr(href)").get()),
                tags=quote.css(".tag *::text").getall(),
            )
            yield item

        yield scrapy.Request(
            response.urljoin(response.css(".next a::attr(href)").get()),
        )
