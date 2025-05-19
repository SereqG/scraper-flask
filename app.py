from flask import Flask, request
from scrapy.crawler import CrawlerProcess
from scraper.booksscraper.booksscraper.spiders.books import BooksSpider

app = Flask(__name__)

@app.route("/scraper")
def scraper():
    print(request.get_json())
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "./output/items.json": {"format": "json"},
            },
        }
    )
    process.crawl(BooksSpider)
    process.start()
    return "scraper"