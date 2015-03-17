from sm.auth.routes import make_routes as auth
from sm.table.routes import make_routes as table


def make_routes(config):
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    auth(config)
    table(config)
    config.add_route('home', '/')
