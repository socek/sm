from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .db import (
    DBSession,
    Base,
    )

from .routes import make_routes


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    make_routes(config)
    config.scan()
    return config.make_wsgi_app()
