import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bnpparibasch.items import Article


class BnpparibaschSpider(scrapy.Spider):
    name = 'bnpparibasch'
    start_urls = ['https://www.bnpparibas.ch/en/news/']

    def parse(self, response):
        links = response.xpath('//a[@class="block-news-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="single__time"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="wysiwyg"]//text()[not(ancestor::div/@class="block-bnpp-push-news")]')\
            .getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
