import logging
import math
from typing import List

log = logging.getLogger(__name__)


class StaticPagination:
    """ pagination class usable when we absolutely know the state of page: items and pages """

    def __init__(
        self, page: int = None, per_page: int = None, items_count: int = None, **kwargs
    ) -> None:
        self.page = page or kwargs.get("page") or 1
        self.per_page = per_page or kwargs.get("per_page") or 25
        self.items_count = items_count

    @property
    def previous_page(self) -> (int, None):
        """ returns the previous page number if it's not the first one """
        if self.page == 1:
            return None
        return self.page - 1

    @property
    def next_page(self) -> (int, None):
        """ returns next page number if it's not the last one (if the results are full)"""
        if self.items_count < self.per_page:
            return None
        return self.page + 1

    @property
    def as_dict(self) -> dict:
        return {
            "page": self.page,
            "previous_page": self.previous_page,
            "next_page": self.next_page,
            "items": self.items_count,
            "per_page": self.per_page,
        }


class DynamicPagination:
    """ pagination class to use when the page and/or item count are not known """

    def __init__(
        self,
        starting_index: int = None,
        per_page: int = None,
        items_count: int = None,
        **kwargs,
    ) -> None:
        self.per_page = per_page or kwargs.get("per_page") or 25

        if kwargs.get("page"):
            self.starting_index = ((kwargs.get("page") - 1) * self.per_page) + 1
        else:
            self.starting_index = starting_index or kwargs.get("starting_index") or 1

        self.items_count = items_count

    @property
    def current_page(self) -> int:
        return math.ceil(int(self.starting_index / self.per_page))

    @property
    def previous_index(self) -> (int, None):
        """ returns the previous page index. returns index or none if this looks like the first page """
        index = self.starting_index - self.per_page
        if index <= 0:
            return None
        return index

    @property
    def next_index(self) -> (int, None):
        """ returns the next starting index or none, if current one looks like the ending one """
        if self.items_count < self.per_page:
            return None
        return self.starting_index + self.per_page

    @property
    def as_dict(self) -> dict:
        return {
            "starting_index": self.starting_index,
            "previous_index": self.previous_index,
            "next_index": self.next_index,
            "items": self.items_count,
            "per_page": self.per_page,
            "page": self.current_page,
        }


class ServiceResult:
    def __init__(
        self, results: list, pagination: (StaticPagination, DynamicPagination)
    ) -> None:
        self.results = results
        self.pagination = pagination

    @property
    def as_dict(self) -> dict:
        return {
            "results": [i.as_dict for i in self.results],
            "pagination": self.pagination.as_dict,
        }


class ErrorResult(Exception):
    """ Class for raising user-visible (public) exceptions. Wrong params, or so """

    def __init__(self, code: str, message: str, instance: object = None) -> None:
        self.code = code
        self.message = message
        self.instance = instance

    def __repr__(self) -> str:
        return f"<ErrorResult {self.code}>"

    @property
    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
        }


class ItemContent:
    def __init__(
        self,
        id: str = None,
        description: str = None,
        url: str = None,
        mimetype: str = None,
    ):
        self.id = id
        self.description = description
        self.url = url
        self.mimetype = mimetype

    def __repr__(self):
        return f"<ItemContent {self.mimetype}: {self.id}>"

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "url": self.url,
            "mimetype": self.mimetype,
        }


class ItemComment:
    pass


class Item:
    def __init__(
        self,
        id: str = None,
        title: str = None,
        description: str = None,
        score: float = None,
        content: List[ItemContent] = None,
        url: str = None,
        comments: List[ItemComment] = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.score = score
        self.content = content
        self.url = url
        self.comments = comments

    def __repr__(self):
        return f"<Item: {self.id}>"

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "score": self.score,
            "content": [c.as_dict for c in self.content] if self.content else None,
            "url": self.url,
            "comments": [c.as_dict for c in self.comments] if self.comments else None,
        }


class ServiceProvider:
    def __init__(self, config: dict):
        self.config = config

    @property
    def service_name(self) -> str:
        """ Service name """
        raise NotImplementedError

    @property
    def service_slug(self) -> str:
        """ Safe service name """
        raise NotImplementedError

    @property
    def service_url(self) -> str:
        """ URL for service base page """
        raise NotImplementedError

    @property
    def pagination_type(self) -> (StaticPagination, DynamicPagination):
        """ Current pagination type. Returns pagination class. """
        raise NotImplementedError

    @property
    def max_score(self) -> (int, float, None):
        """
            Set max score for service provider.
            If platform supports star-based rating, e.g. 6.5/10, set this to its maximum.
            Otherwise, if platform doesn't have maximum score - set to None (default)
        """
        return None
