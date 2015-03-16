import colander


class LoginForm(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())
