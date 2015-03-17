def make_routes(config):
    config.add_route('table_add', '/table/add/{width:\d+}/{height:\d+}')
    config.add_route('table_list', '/table')
