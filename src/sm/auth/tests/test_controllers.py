from pytest import fixture, yield_fixture
from mock import MagicMock, patch
from sqlalchemy.orm.exc import NoResultFound
from deform import ValidationFailure

from ..models import NotLoggedUser
from ..controllers import AuthController, LoginController, AfterLoginController


class LocalFixtures(object):

    @fixture
    def request(self):
        request = MagicMock()
        request.session = {}
        return request

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

    @yield_fixture
    def is_logged(self, ctrl):
        with patch.object(ctrl, '_is_logged') as mock:
            yield mock

    @yield_fixture
    def found(self):
        with patch('sm.auth.controllers.HTTPFound') as mock:
            yield mock


class TestAuthController(LocalFixtures):

    @fixture
    def ctrl(self, request):
        return AuthController(request)

    def test_get_logged_user_from_cache(self, request, ctrl):
        """
        .get_logged_user should return user which is already in the cache.
        """
        fake_user = MagicMock()
        ctrl._cache['user'] = fake_user

        assert ctrl.get_logged_user() == fake_user

    def test_get_logged_user_from_db(self, request, ctrl, db, session):
        """
        .get_logged_user should return user from db if proper data was set in
        the session
        """
        session['user_id'] = 10
        user = db.query.return_value.filter_by.return_value.one.return_value

        assert ctrl.get_logged_user() == user
        db.query.return_value.filter_by.assert_called_once_with(id=10)

    def test_get_logged_user_db_not_found(self, request, ctrl, db, session):
        """
        .get_logged_user should return NotLoggedUser when user_id not found in
        the db
        """
        session['user_id'] = 15
        one_method = db.query.return_value.filter_by.return_value.one
        one_method.side_effect = NoResultFound

        assert type(ctrl.get_logged_user()) == NotLoggedUser
        db.query.return_value.filter_by.assert_called_once_with(id=15)

    def test_get_logged_user_not_fround(self, request, ctrl):
        """
        .get_logged_user should return NotLoggedUser when no user_id is set
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
        ._is_logged should return True whenever user has one of this
        permissions:
            * logged
            * administrator
        """
        user.permission = 'my permission'
        assert ctrl._is_logged() is False

        user.permission = 'logged'
        assert ctrl._is_logged() is True

        user.permission = 'administrator'
        assert ctrl._is_logged() is True


class TestLoginController(LocalFixtures):

    @fixture
    def ctrl(self, request):
        return LoginController(request)

    @yield_fixture
    def process_form(self, ctrl):
        with patch.object(ctrl, 'process_form') as mock:
            yield mock

    @yield_fixture
    def schema(self):
        with patch('sm.auth.controllers.LoginForm') as mock:
            yield mock

    @yield_fixture
    def form(self):
        with patch('sm.auth.controllers.Form') as mock:
            yield mock

    @yield_fixture
    def data(self, ctrl):
        with patch.object(ctrl, 'get_form_data') as mock:
            yield mock

    @yield_fixture
    def submit_form(self, ctrl):
        with patch.object(ctrl, 'submit_form') as mock:
            yield mock

    def test_call_not_logged(self, request, ctrl, is_logged, process_form):
        """
        LoginController should proccess form and return context
        if user is not logged.
        """
        is_logged.return_value = None

        context = ctrl()

        process_form.assert_called_once_with()
        assert context == {'error': None}

    def test_call_logged(self, request, ctrl, is_logged, process_form, found):
        """
        LoginController should proccess form and redirect to auth_after_login
        route if user has logged during the process.
        """
        is_logged.return_value = True

        context = ctrl()

        process_form.assert_called_once_with()
        found.assert_called_once_with(
            location=request.route_path.return_value
        )
        request.route_path.assert_called_once_with('auth_after_login')
        assert context == found.return_value

    def test_proccess_form(self, ctrl, schema, form, data, submit_form):
        """
        .process_form should create form object, gather data and put them into
        context.
        """
        ctrl.process_form()

        schema.assert_called_once_with()
        form.assert_called_once_with(schema.return_value, buttons=('submit',))

        assert ctrl.context['form'] == form.return_value.render.return_value
        form.return_value.render.assert_called_once_with()
        assert ctrl.context['values'] == data.return_value
        submit_form.assert_called_once_with(data.return_value)

    def test_get_form_data_on_submit(self, ctrl, request):
        """
        .get_form_data should gather data from form
        """
        form = MagicMock()
        form.validate.return_value = {
            'name': 'myname',
            'password': 'pass'
        }
        request.POST = {'submit': True}

        data = ctrl.get_form_data(form)

        form.validate.assert_called_once_with(request.POST.items())
        assert data == form.validate.return_value

    def test_get_form_data_on_error(self, ctrl, request):
        """
        .get_form_data should return False if there was an error in the form
        validation.
        """
        form = MagicMock()
        form.validate.side_effect = ValidationFailure(
            MagicMock(), MagicMock(), MagicMock())
        request.POST = {'submit': True}

        data = ctrl.get_form_data(form)

        form.validate.assert_called_once_with(request.POST.items())
        assert data is False

    def test_get_form_data_on_no_submit(self, ctrl):
        """
        .get_form_data should return None if no submit was made.
        """
        form = MagicMock()

        assert ctrl.get_form_data(form) is None

    def test_submit_form(self, ctrl, db):
        """
        .submit_form should do nothing if no values is set
        """
        ctrl.submit_form(None)

        assert db.query.called is False

    def test_submit_form_when_wrong_name(self, ctrl, session, db):
        """
        .submit_form should put error in context when submitted wrong name for
        user
        """
        one = db.query.return_value.filter.return_value.one
        one.side_effect = NoResultFound

        ctrl.submit_form({
            'name': 'wrong',
            'password': 'do not matter',
        })

        assert ctrl.context == {'error': 'Wrong name or password!'}

    def test_submit_form_when_wrong_password(self, ctrl, session, db):
        """
        .submit_form should put error in context when submitted wrong password
        for user.
        """
        one = db.query.return_value.filter.return_value.one
        user = one.return_value
        user.password = 'good password'

        ctrl.submit_form({
            'name': 'good',
            'password': 'wrong',
        })

        assert ctrl.context == {'error': 'Wrong name or password!'}

    def test_submit_form_when_good(self, ctrl, session, db):
        """
        .submit_form should put user_id in context when submitted good name and
        password for user.
        """
        one = db.query.return_value.filter.return_value.one
        user = one.return_value
        user.password = 'good password'

        ctrl.submit_form({
            'name': 'good',
            'password': 'good password',
        })

        assert ctrl.context == {'error': None}
        assert session['user_id'] == user.id


class TestAfterLoginControllerController(LocalFixtures):

    @fixture
    def ctrl(self, request):
        return AfterLoginController(request)

    @yield_fixture
    def user(self, ctrl):
        with patch.object(ctrl, 'get_logged_user') as mock:
            yield mock

    def test_when_not_loggedin(self, ctrl, is_logged, found, request):
        """
        AfterLoginController should redirect to login page when user is not
        logged in.
        """
        is_logged.return_value = False

        assert ctrl() == found.return_value
        found.assert_called_once_with(
            location=request.route_path.return_value
        )
        request.route_path.assert_called_once_with('auth_login')

    def test_when_loggedin(self, ctrl, is_logged, user):
        """
        AfterLoginController should put logged in user into context.
        """
        is_logged.return_value = True

        assert ctrl() == {
            'error': None,
            'user': user.return_value
        }
