import scrapy
import urllib.parse
from linkedinjobscraper.items import LinkedinjobscraperItem


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
        base_url = "https://www.linkedin.com/jobs/search?keywords=Web%20Developer&location=United%20States&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
        # query_params = {
        #     "keywords": "developer",
        #     "location": "United States",
        #     "position": 1,
        #     "pageNum": 0,
        # }
        # url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
        # print(url)
        yield scrapy.Request(
            base_url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                # playwright_page_methods=[
                #     PageMethod("wait_for_selector", "ul>li"),
                #     PageMethod(
                #         "evaluate", "window.scrollBy(0,document.body.scrollHeight)"
                #     ),
                #     PageMethod("wait_for_selector", "ul>li:nth-child(60)"),
                # ],
                errback=self.errorback,
            ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        prev_scroll_height = 0
        new_scroll_height = await page.evaluate("document.body.scrollHeight")
        while prev_scroll_height != new_scroll_height:
            await page.evaluate("window.scrollBy(0,document.body.scrollHeight)")
            await page.wait_for_selector("ul>li:last-child")
            prev_scroll_height = new_scroll_height
            new_scroll_height = await page.evaluate("document.body.scrollHeight")

        content = await page.content()
        response = response.replace(body=content)
        await page.close()
        job_list = response.xpath("//section/ul[@class='jobs-search__results-list']/li")
        print(len(job_list))
        # print(list[0].xpath(".//span/text()").get())
        job_item = LinkedinjobscraperItem()
        for job in job_list:
            job_item["title"] = (
                job.xpath(".//h3[@class='base-search-card__title']/text()")
                .get()
                .strip()
            )
            job_item["job_url"] = job.xpath(".//div/a/@href").get().strip()
            job_item["company_name"] = (
                job.xpath(".//h4[@class='base-search-card__subtitle']/a/text()")
                .get()
                .strip()
            )
            job_item["company_url"] = (
                job.xpath(".//h4[@class='base-search-card__subtitle']/a/@href")
                .get()
                .strip()
            )
            job_item["location"] = (
                job.xpath(".//span[@class='job-search-card__location']/text()")
                .get()
                .strip()
            )
            yield job_item

    async def errorback(self, faliure):
        page = faliure.request.meta["playwright_page"]
        await page.close()
