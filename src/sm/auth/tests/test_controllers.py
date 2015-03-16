from pytest import fixture, yield_fixture
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound

from ..models import NotLoggedUser
from ..controllers import AuthController


class TestHomeController(object):

    @fixture
    def request(self):
        request = MagicMock()
        request.session = {}
        return request

    @fixture
    def ctrl(self, request):
        return AuthController(request)

    @yield_fixture
    def db(self, ctrl):
        with patch.object(ctrl, 'db') as mock:
            yield mock

    @fixture
    def session(self, request):
        return request.session

    @fixture
    def user(self, ctrl):
        ctrl._cache['user'] = NotLoggedUser()
        return ctrl._cache['user']

    def test_get_logged_user_from_cache(self, request, ctrl):
        """
        get_logged_user should return user which is already in the cache.
        """
        fake_user = MagicMock()
        ctrl._cache['user'] = fake_user

        assert ctrl.get_logged_user() == fake_user

    def test_get_logged_user_from_db(self, request, ctrl, db, session):
        """
        get_logged_user should return user from db if proper data was set in
        the session
        """
        session['user_id'] = 10
        user = db.query.return_value.filter_by.return_value.one.return_value

        assert ctrl.get_logged_user() == user
        db.query.return_value.filter_by.assert_called_once_with(id=10)

    def test_get_logged_user_db_not_found(self, request, ctrl, db, session):
        """
        get_logged_user should return NotLoggedUser when user_id not found in
        the db
        """
        session['user_id'] = 15
        one_method = db.query.return_value.filter_by.return_value.one
        one_method.side_effect = NoResultFound

        assert type(ctrl.get_logged_user()) == NotLoggedUser
        db.query.return_value.filter_by.assert_called_once_with(id=15)

    def test_get_logged_user_not_fround(self, request, ctrl):
        """
        get_logged_user should return NotLoggedUser when no user_id is set
        """

        assert type(ctrl.get_logged_user()) == NotLoggedUser

    def test_has_permission(self, ctrl, user):
        """
        has_permission should return if user has a permission
        """
        user.permission = 'my permission'

        assert ctrl.has_permission('my permission') is True
        assert ctrl.has_permission('not my permission') is False

    def test_is_logged(self, ctrl, user):
        """
        _is_logged should return True whenever user has one of this permissions
        * logged
        * administrator
        """
        user.permission = 'my permission'
        assert ctrl._is_logged() is False

        user.permission = 'logged'
        assert ctrl._is_logged() is True

        user.permission = 'administrator'
        assert ctrl._is_logged() is True
