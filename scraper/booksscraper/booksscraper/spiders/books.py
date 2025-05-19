import scrapy
from scrapy.crawler import CrawlerProcess

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    process = CrawlerProcess(
    settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
    }
)

    price_min=None
    price_max=None
    rating_min=None
    rating_max=None

    def __init__(self, price_min=None, price_max=None, rating_min=None, rating_max=None, *args, **kwargs):
        if price_min:
            self.price_min = float(price_min)
        if price_max:
            self.price_max = float(price_max)
        if rating_min:
            self.rating_min = int(rating_min)
        if rating_max:
            self.rating_max = int(rating_max)


    def check_conditions(self, book):
        if self.price_min is not None and book["price"] < self.price_min:
            return False
        if self.price_max is not None and book["price"] > self.price_max:
            return False
        if self.rating_min is not None and book["rating"] < self.rating_min:
            return False
        if self.rating_max is not None and book["rating"] < self.rating_max:
            return False
        return True


    def parse(self, response):
        rates = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5
        }
        books = response.css(".product_pod")

        next_link = response.css(".next a").attrib["href"]

        for book in books:
            price = book.css(".price_color::text").get()
            title = book.css("h3 a::text").get()
            rating = book.css(".star-rating").attrib["class"].split(" ")[1].lower()

            should_save_book = self.check_conditions({
                "price": float(price.split("£")[1]),
                "rating": rates[rating]
                })
            
            if should_save_book:
                yield {
                    "price": float(price.split("£")[1]),
                    "title": title,
                    "rating": rating,
                    "link": book.css("h3 a").attrib["href"]
                }

        if next_link is not None:
            yield response.follow(next_link, callback=self.parse)
