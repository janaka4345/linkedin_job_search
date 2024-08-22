import scrapy
import urllib.parse
from scrapy_playwright.page import PageMethod


def should_abort_request(request):
    if request.resource_type == "image":
        return True
    if request.resource_type == "stylesheet":
        return True
    return False


class LinkedinjobspiderSpider(scrapy.Spider):
    name = "linkedinjobspider"
    allowed_domains = ["linkedin.com"]
    # start_urls = ["linkedin.com"]
    custom_settings = {"PLAYWRIGHT_ABORT_REQUEST": should_abort_request}

    def start_requests(self):
        base_url = "https://www.linkedin.com/jobs/search?keywords=developer&location=United%20States&position=1&pageNum=0"
        query_params = {
            "keywords": "developer",
            "location": "United States",
            "position": 1,
            "pageNum": 0,
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
        print(url)
        yield scrapy.Request(
            base_url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod("wait_for_selector", "ul>li"),
                    PageMethod(
                        "evaluate", "window.scrollBy(0,document.body.scrollHeight)"
                    ),
                    PageMethod("wait_for_selector", "ul>li:nth-child(60)"),
                ],
                errback=self.errorback,
            ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        # await page.wait_until("networkidle")
        list = response.xpath("//section/ul/li/div/a")
        print(len(list))
        print(list[0].xpath(".//span/text()").get())
        yield None

    async def errorback(self, faliure):
        page = faliure.request.meta["playwright_page"]
        await page.close()
