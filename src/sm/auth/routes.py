def make_routes(config):
    config.add_route('auth_login', '/auth')
    config.add_route('auth_after_login', '/auth/after')
