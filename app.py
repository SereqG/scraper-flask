from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scraper.booksscraper.booksscraper.spiders.books import BooksSpider

import json
import uuid
import os

app = Flask(__name__)

@app.route("/scraper")
def scraper():
    job_id = str(uuid.uuid4())
    output_path = f"./output/{job_id}.json"
    req = request.get_json()
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                output_path: {"format": "json"},
            },
        }
    )
    process.crawl(BooksSpider, request_body = req)
    process.start()

    return jsonify({"status": "end", "job_id": job_id}), 202


@app.route("/results/<job_id>")
def get_results(job_id):
    path = f"./output/{job_id}.json"
    if not os.path.exists(path):
        return jsonify({"status": "pending or not found"}), 404
    with open(path, "r") as f:
        return jsonify(json.load(f))