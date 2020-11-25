from typing import Any, Dict, Generator, Union

import extruct

from lib.normalise import datetime_from_iso_utc, html2plain


class Datasource:
    name = "microdata"

    def extract(
        self, html: Union[bytes, str], base_url: str, view_date
    ) -> Generator[Dict[Any, Any], None, None]:
        data = extruct.extract(html, base_url, syntaxes=["microdata"])["microdata"]
        job_posts = [
            datum["properties"]
            for datum in data
            if datum["type"] == "http://schema.org/JobPosting"
        ]
        for post in job_posts:
            yield {"data": post, "uri": base_url, "view_date": view_date}

    def normalise(self, data, uri, view_date):
        org = data["hiringOrganization"]
        if isinstance(org, dict):
            org = org.get("name")
        if not isinstance(org, str):
            org = None
        return {
            "title": data["title"],
            "description": html2plain(data["description"]),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": org,
        }
