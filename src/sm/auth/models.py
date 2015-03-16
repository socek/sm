from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from sm.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    password = Column(Text)
    permission = Column(Text)


class NotLoggedUser(User):
    id = None
    name = None
    password = None
    permission = 'not logged'
