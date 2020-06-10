import logging
import os

from requests import Response
from requests_html import HTMLSession, HTMLResponse

from memapi import ServiceProvider
from memapi.services import (
    StaticPagination,
    DynamicPagination,
    ServiceResult,
    Item,
    ItemContent,
)

log = logging.getLogger(__name__)


class Repostuj(ServiceProvider):
    def __init__(self):
        super().__init__()
        self.session: HTMLSession = HTMLSession()

    @property
    def service_name(self) -> str:
        return "Repostuj"

    @property
    def service_slug(self) -> str:
        return "repostuj"

    @property
    def service_url(self) -> str:
        return "https://repostuj.pl"

    @property
    def pagination_type(self) -> (StaticPagination, DynamicPagination):
        return DynamicPagination

    @property
    def max_score(self) -> (int, float, None):
        return None

    def action_main(self, pagination: dict = None) -> ServiceResult:
        """ Returns mainpage results """
        pagination = DynamicPagination(**(pagination or dict()))

        return self._grabber("?top", pagination)

    def action_top(self, pagination: dict = None) -> ServiceResult:
        """ Returns the results from "top" category """
        pagination = DynamicPagination(**(pagination or dict()))

        return self._grabber("popularne/", pagination)

    # def action_tag(self, tag_name: str, pagination: dict = None) -> ServiceResult:
    #     """ Returns the results per tag """
    #     raise NotImplementedError  # TODO: sometimes in the future
    #
    # def action_author(self, author_name:str, pagination:dict=None) -> ServiceResult:
    #     """ Returns the results per author """
    #     raise NotImplementedError  # TODO: sometimes in the future

    def action_single(self, item_id: str):
        """ Get single item by Item ID """
        response = self.session.get(f"{self.service_url}/post/{item_id}")
        current = self._parse_html(response)

        return ServiceResult(
            result=[current],
            pagination=DynamicPagination(starting_index=1, per_page=1, items_count=1),
        )

    def _grabber(self, url: str, pagination: DynamicPagination) -> ServiceResult:
        per_page = pagination.per_page
        starting_index = pagination.starting_index

        url = f"https://repostuj.pl/{url}"
        elements = []
        start_returning_from = starting_index
        counter = 0

        while True:
            # make request
            response: Response = self.session.get(url)

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
                elements[-1].title == current.title and elements[-1] == current.item_id
            ):
                log.debug(
                    f"Found {len(elements)} for required {per_page}, returning results"
                )
                break

            # append current element to list
            log.info(f"Found {current} via {self.__class__.__name__}")
            elements.append(current)

            # break if we got enough elements
            if per_page and len(elements) >= per_page:
                log.debug(f"Hit {per_page} elements limit, breaking")
                break

        log.debug(f"Found total of {len(elements)} elements")
        return ServiceResult(
            result=elements,
            pagination=DynamicPagination(
                starting_index=start_returning_from,
                per_page=pagination.per_page,
                items_count=len(elements),
            ),
        )

    def _parse_html(self, response: Response):
        return Item(
            id=self._get_id(response.html),
            title=self._get_title(response.html),
            description=None,
            score=self._get_score(response.html),
            content=self._get_content(response.html),
            url=self._get_url(response.html),
            comments=[],  # TODO later
        )

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
                items.append(
                    ItemContent(
                        id=self._get_id_from_filename(i.attrs.get("src")),
                        description=None,
                        url=f"https://repostuj.pl{i.attrs.get('src')}",
                        mimetype=self._mimetype_from_ext(i.attrs.get("src")),
                    )
                )

        # grab all the videos
        if videos:
            for v in videos:
                source_tag = [
                    e
                    for e in filter(
                        lambda el: el.attrs.get("type") == "video/mp4",
                        [v] if not isinstance(v, list) else v,
                    )
                ]
                if len(source_tag):
                    source_tag = source_tag[0]
                    log.debug(
                        f"Found video {source_tag.attrs.get('src')} for {page.url}"
                    )
                    items.append(
                        ItemContent(
                            id=self._get_id_from_filename(source_tag.attrs.get("src")),
                            description=None,
                            url=f"https://repostuj.pl{source_tag.attrs.get('src')}",
                            mimetype=self._mimetype_from_ext(
                                source_tag.attrs.get("src")
                            ),
                        )
                    )

        return items

    def _get_url(self, page: HTMLResponse) -> str:
        """ get current url """
        return page.find("meta[property='og:url']", first=True).attrs.get("content")

    def _get_next_url(self, page: HTMLResponse) -> str:
        """ get next page's url """
        return f"https://repostuj.pl{page.find('#post-prev-btn', first=True).attrs.get('href')}"

    def _get_id_from_filename(self, filename: str) -> str:
        basename = os.path.basename(filename)
        name, ext = os.path.splitext(basename)

        return name.lower()

    def _mimetype_from_ext(self, filename: str) -> str:
        extensions = {
            "mp4": "video/mp4",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
            "webm": "video/webm",
        }

        name, ext = os.path.splitext(filename.lower())
        return extensions.get(ext)
