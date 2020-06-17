import unittest

from memapi.services.repostuj import Repostuj
from memapi.services import DynamicPagination, StaticPagination, ServiceResult, Item


class TestRepostuj(unittest.TestCase):
    def test_service_name(self):
        svc = Repostuj(config=dict())

        assert svc.service_name is not None

    def test_service_slug(self):
        svc = Repostuj(config=dict())

        assert svc.service_slug is not None

    def test_service_url(self):
        svc = Repostuj(config=dict())

        assert svc.service_url is not None
        assert "http" in svc.service_url

    def test_pagination_type(self):
        svc = Repostuj(config=dict())

        assert svc.pagination_type in (DynamicPagination, StaticPagination)

    def test_max_score(self):
        svc = Repostuj(config=dict())

        assert type(svc.max_score) in (type(None), float, int)

    def _the_test_for_actions(self, call):
        assert isinstance(call, ServiceResult)
        assert isinstance(call.pagination, (DynamicPagination, StaticPagination))
        assert 0 < len(call.results)
        assert len(call.results) == 5

        for i in call.results:
            assert isinstance(i, Item)

    def test_action_main(self):
        svc = Repostuj(config=dict())

        pagination = {"page": 1, "per_page": 5}
        call = svc.action_main(pagination=pagination)

        self._the_test_for_actions(call)

    def test_action_top(self):
        svc = Repostuj(config=dict())

        pagination = {"page": 1, "per_page": 5}
        call = svc.action_top(pagination=pagination)

        self._the_test_for_actions(call)

    def test_action_single(self):
        svc = Repostuj(config=dict())

        pagination = {"page": 1, "per_page": 5}
        main_call = svc.action_main(pagination=pagination)

        item_id = main_call.results[0].id
        call = svc.action_single(item_id=item_id)

        assert main_call.results[0].id == call.results[0].id

        assert isinstance(call.pagination, DynamicPagination)
        assert call.pagination.current_page == 1
        assert call.pagination.per_page == 1
