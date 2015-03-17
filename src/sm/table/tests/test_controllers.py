from pytest import fixture, yield_fixture
from mock import patch

from ..models import Table
from ..controllers import AddController, ListController
from sm.auth.tests.test_controllers import GlobalFixtures


class LocalFixtures(GlobalFixtures):

    @yield_fixture
    def tablecls(self):
        with patch('sm.table.controllers.Table') as mock:
            yield mock


class TestAddController(LocalFixtures):

    @fixture
    def matchdict(self, request, ctrl):
        request.matchdict = {}
        ctrl.matchdict = request.matchdict
        return request.matchdict

    @yield_fixture
    def datetime(self):
        with patch('sm.table.controllers.datetime') as mock:
            yield mock

    @fixture
    def ctrl(self, request):
        return AddController(request)

    def test_adding(self, matchdict, request, ctrl, tablecls, datetime, db):
        """
        AddController should create Table instance with actual time in
        isoformat, user_agent returned by request and window_size generated
        from matchdict. This instance should also be added to database, and its
        dict representation should be returned to json.
        """
        matchdict['width'] = '100'
        matchdict['height'] = '150'
        table = tablecls.return_value

        assert ctrl() == {
            'status': 'ok',
            'object': table.to_dict.return_value,
        }

        tablecls.assert_called_once_with(
            timestamp=datetime.now.return_value.isoformat.return_value,
            user_agent=request.user_agent,
            window_size='100x150')
        db.add.assert_called_once_with(table)
        db.flush.assert_called_once_with()


class TestListController(LocalFixtures):

    @yield_fixture
    def get_all_objects(self, ctrl):
        with patch.object(ctrl, 'get_all_objects') as mock:
            yield mock

    @fixture
    def ctrl(self, request):
        return ListController(request)

    def test_call(self, ctrl, get_all_objects):
        """
        ListController should generate list of all Table items from db.
        """
        assert ctrl() == {
            'objects': get_all_objects.return_value,
        }
        get_all_objects.assert_called_once_with()

    def test_get_all_objects(self, ctrl, db):
        """
        .get_all_objects should return generator of all Table items from db.
        """
        assert ctrl.get_all_objects() == db.query.return_value
        db.query.assert_called_once_with(Table)
