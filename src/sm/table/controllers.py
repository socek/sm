from pyramid.view import view_config
from datetime import datetime

from sm.db import DBSession
from .models import Table


class TableController(object):

    def __init__(self, request):
        self.request = request
        self.context = {}
        self.route = request.route_path
        self.db = DBSession
        self.session = self.request.session
        self.matchdict = request.matchdict


@view_config(route_name='table_add', renderer='json')
class AddController(TableController):

    def __call__(self):
        table = Table(
            timestamp=datetime.now().isoformat(),
            user_agent=self.request.user_agent,
            window_size='%(width)sx%(height)s' % self.matchdict,
        )
        self.db.add(table)
        self.db.flush()
        return {'status': 'ok', 'object': table.to_dict()}


@view_config(route_name='table_list', renderer='templates/table/list.jinja2')
class ListController(TableController):

    def __call__(self):
        self.context['objects'] = self.get_all_objects()

        return self.context

    def get_all_objects(self):
        return self.db.query(Table)
