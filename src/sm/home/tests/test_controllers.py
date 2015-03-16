from pytest import fixture
from mock import MagicMock

from ..controllers import home


class TestHomeController(object):

    @fixture
    def request(self):
        return MagicMock()

    def test_controller(self, request):
        """
        home controller should return only empty dict, because it's only static
        site.
        """
        result = home(request)

        assert result == {}
