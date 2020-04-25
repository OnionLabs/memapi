import logging
import os

from requests import Response
from requests_html import HTMLSession, HTMLResponse
from memapi.services import ServiceProvider

log = logging.getLogger(__name__)


class Repostuj(ServiceProvider):
    SERVICE_NAME = "Repostuj"
    SERVICE_DOMAIN = "repostuj.pl"

    def __init__(self):
        super().__init__()
        self.session = HTMLSession()

    @property
    def allowed_actions(self) -> list:
        return ["main", "top", "single", "by_tag", "by_author"]

    def action_main(self, page: int = 1, per_page: int = 25) -> dict:
        """ grab all elements from the "main" section """
        return {"results": self._grab_paginated("?top", page, per_page)}

    def action_top(self, page: int = 1, per_page: int = 25) -> dict:
        """ grab all elements from the "top" section """
        return {"results": self._grab_paginated("popularne/", page, per_page)}

    def action_single(self, item_id: str) -> dict:
        """ Get single element by item_id """

        url = f"https://repostuj.pl/post/{item_id}"
        response = self.session.get(url)
        current = self._parse_html(response)

        return {"results": [current]}

    def action_by_tag(self, tag_name):
        pass

    def action_by_author(self, author_name):
        pass

    def _grab_paginated(self, starting_url: str, page: int, per_page: int) -> list:
        # change type of params
        per_page = int(per_page) if isinstance(per_page, str) else per_page
        page = int(page) if isinstance(page, str) else page

        url = f"https://repostuj.pl/{starting_url}"
        elements = []
        start_returning_from = (page - 1) * per_page
        counter = 0

        while True:
            # make request
            response = self.session.get(url)

            # get next url from current's response's html
            url = self._get_next_url(response.html)

            # this service hasn't got pagination - every page is a single item here
            # sadly, we need to iterate over all elements and just start returning them from the requested one
            counter += 1
            if counter < start_returning_from:
                continue

            # parse current element
            current = self._parse_html(response)

            # if last element's title is same as current one it means, that we hit the last one - break
            if elements and (
                elements[-1].get("title") == current.get("title") and elements[-1] == current.get("item_id")
            ):
                log.debug(f"Found {len(elements)} for required {per_page}, returning results")
                break

            # append current element to list
            log.info(f"Found {current} via {self.__class__.__name__}")
            elements.append(current)

            # break if we got enough elements
            if per_page and len(elements) >= per_page:
                log.debug(f"Hit {per_page} elements limit, breaking")
                break

        log.debug(f"Found total of {len(elements)} elements")
        return elements

    def _parse_html(self, resp: Response) -> dict:
        """ parse html page to dict item """
        return {
            "id": self._get_id(resp.html),
            "title": self._get_title(resp.html),
            "description": None,
            "score": self._get_score(resp.html),
            "content": self._get_content(resp.html),
            "url": self._get_url(resp.html),
        }

    def _get_id(self, page: HTMLResponse) -> str:
        """ get item id """
        return page.find("#commentBox", first=True).attrs.get("data-slug")

    def _get_title(self, page: HTMLResponse) -> str:
        """ get item title """
        return page.find("span.title", first=True).text.split(" | ")[1]

    def _get_score(self, page: HTMLResponse):
        """ get item rating """
        return page.find("span.vote-count", first=True).attrs.get("data")

    def _get_content(self, page: HTMLResponse) -> (str, None):
        """ get contents: videos, images, etc """
        images = page.find("div.img-block img.img-fluid")
        videos = page.find("div.vid-block source")
        items = []

        # grab all the images
        if images:
            for i in images:
                log.debug(f"Found image {i.attrs.get('src')} for {page.url}")
                items.append(f"https://repostuj.pl{i.attrs.get('src')}")

        # grab all the videos
        if videos:
            for v in videos:
                source_tag = [
                    e
                    for e in filter(
                        lambda el: el.attrs.get("type") == "video/mp4", [v] if not isinstance(v, list) else v
                    )
                ]
                if len(source_tag):
                    source_tag = source_tag[0]
                    log.debug(f"Found video {source_tag.attrs.get('src')} for {page.url}")
                    items.append(f"https://repostuj.pl{source_tag.attrs.get('src')}")

        return items

    def _get_url(self, page: HTMLResponse) -> str:
        """ get current url """
        return page.find("meta[property='og:url']", first=True).attrs.get("content")

    def _get_next_url(self, page: HTMLResponse) -> str:
        """ get next page's url """
        return f"https://repostuj.pl{page.find('#post-prev-btn', first=True).attrs.get('href')}"
