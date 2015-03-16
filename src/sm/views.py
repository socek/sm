from pyramid.view import view_config

from .models import (
    DBSession,
    MyModel,
)


@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def home(request):
    one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    return {'one': one, 'project': 'sm'}
