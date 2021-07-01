import extruct

from job_pipeline.lib.normalise import datetime_from_iso_utc, html2plain
from job_pipeline.sources.abstract_datasource import module_name
from job_pipeline.sources.commoncrawl_datasource import CommonCrawlDatasource


class Datasource(CommonCrawlDatasource):
    name = module_name(__name__)

    def extract(self, html: bytes, base_url: str, view_date):
        data = extruct.extract(html, base_url, syntaxes=["microdata"])["microdata"]
        job_posts = [
            datum["properties"]
            for datum in data
            if datum["type"] == "http://schema.org/JobPosting"
        ]
        return [
            {"data": post, "uri": base_url, "view_date": view_date}
            for post in job_posts
        ]

    def normalise(self, data, uri, view_date):
        org = data["hiringOrganization"]
        if isinstance(org, dict):
            org = org.get("name")
        if not isinstance(org, str):
            org = None
        return {
            "title": data["title"],
            "description": html2plain(data.get("description", "")),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": org,
        }
