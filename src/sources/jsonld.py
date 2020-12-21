import extruct
from lib.normalise import datetime_from_iso_utc, html2plain
from sources.abstract_datasource import module_name
from sources.commoncrawl_datasource import CommonCrawlDatasource


class Datasource(CommonCrawlDatasource):
    name = module_name(__name__)

    def extract(self, html: bytes, base_url: str, view_date):
        data = extruct.extract(html, base_url, syntaxes=["json-ld"])["json-ld"]
        job_posts = [datum for datum in data if datum["@type"] == "JobPosting"]
        return [
            {"data": post, "uri": base_url, "view_date": view_date}
            for post in job_posts
        ]

    def normalise(self, data, uri, view_date):
        if "description" in data:
            description = html2plain(data["description"])
        else:
            description = None
        return {
            "title": data["title"],
            "description": description,
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": data.get("hiringOrganization"),
        }
