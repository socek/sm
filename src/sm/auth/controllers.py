from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure
from sqlalchemy.orm.exc import NoResultFound

from sm.db import DBSession
from .forms import LoginForm
from .models import User, NotLoggedUser


class AuthController(object):

    def __init__(self, request):
        self.request = request
        self._cache = {}
        self.context = {
            'error': None,
        }
        self.route = request.route_path
        self.db = DBSession
        self.session = self.request.session

    def get_logged_user(self):
        if 'user' in self._cache:
            return self._cache['user']
        elif self._is_user_id():
            try:
                self._cache['user'] = (
                    self.db.query(User)
                    .filter_by(id=self.session['user_id'])
                    .one()
                )
            except NoResultFound:
                self._cache['user'] = NotLoggedUser()
        else:
            self._cache['user'] = NotLoggedUser()

        return self._cache['user']

    def has_permission(self, permission):
        return self.get_logged_user().permission == permission

    def _is_user_id(self):
        return 'user_id' in self.session

    def _is_logged(self):
        return (
            self.has_permission('logged')
            or self.has_permission('administrator')
        )


@view_config(route_name='auth_login', renderer='templates/auth/login.jinja2')
class Login(AuthController):

    def __call__(self):
        self.process_form()

        if self._is_logged():
            return HTTPFound(location=self.route('auth_after_login'))

        return self.context

    def process_form(self):
        schema = LoginForm()
        form = Form(schema, buttons=('submit',))
        values = self.get_form_data(form)
        if values:
            self.submit_form(values)

        self.context['form'] = form.render()
        self.context['values'] = values

    def get_form_data(self, form):
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure:
                return False

            return {
                "name": appstruct['name'],
                "password": appstruct['password'],
            }
        else:
            return None

    def submit_form(self, values):
        session = self.request.session

        try:
            user = (
                self.db.query(User)
                .filter(User.name == values['name'])
                .one()
            )
            if user.password == values['password']:
                session['user_id'] = user.id
            else:
                self.context['error'] = 'Wrong name or password!'
        except NoResultFound:
            self.context['error'] = 'Wrong name or password!'


@view_config(
    route_name='auth_after_login',
    renderer='templates/auth/after_login.jinja2')
class AfterLogin(AuthController):

    def __call__(self):
        if not self._is_logged():
            return HTTPFound(location=self.route('auth_login'))

        self.context['user'] = self.get_logged_user()

        return self.context
