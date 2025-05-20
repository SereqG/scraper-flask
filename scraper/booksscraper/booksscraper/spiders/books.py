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

    def __init__(self, request_body, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_min = request_body["price_min"]
        self.price_max = request_body["price_max"]
        self.rating_min = request_body["rating_min"]
        self.rating_max = request_body["rating_max"]


    def check_conditions(self, book):
        if self.price_min is not None and book["price"] < self.price_min:
            return False
        if self.price_max is not None and book["price"] > self.price_max:
            return False
        if self.rating_min is not None and book["rating"] < self.rating_min:
            return False
        if self.rating_max is not None and book["rating"] > self.rating_max:
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

        next_page = response.css(".next a")
        next_link = next_page.attrib.get("href") if next_page else None

        for book in books:
            price_text = book.css(".price_color::text").get()
            title = book.css("h3 a::attr(title)").get()
            rating_class = book.css(".star-rating").attrib.get("class", "")
            rating_value = rating_class.split(" ")[1].lower() if len(rating_class.split(" ")) > 1 else "zero"

            price = float(price_text.replace("£", "")) if price_text else 0.0
            rating = rates.get(rating_value, 0)

            should_save_book = self.check_conditions({
                "price": price,
                "rating": rating
            })

            if should_save_book:
                link = book.css("h3 a::attr(href)").get()
                if "catalogue" in link:
                    link = f"https://books.toscrape.com/{link}"
                else:
                    link = f"https://books.toscrape.com/catalogue/{link}"
                yield {
                    "price": price,
                    "title": title,
                    "rating": rating,
                    "link": link
                }

        if next_link:
            yield response.follow(next_link, callback=self.parse)
