from typing import Any, Dict, Generator, Union

import extruct

from lib.normalise import datetime_from_iso_utc, html2plain


class Datasource:
    name = "jsonld"

    def extract(
        self, html: Union[bytes, str], base_url: str, view_date
    ) -> Generator[Dict[Any, Any], None, None]:
        data = extruct.extract(html, base_url, syntaxes=["json-ld"])["json-ld"]
        job_posts = [datum for datum in data if datum["@type"] == "JobPosting"]
        for post in job_posts:
            yield {"data": post, "uri": base_url, "view_date": view_date}

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
