from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from sm.db import Base


class Table(Base):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Text)
    user_agent = Column(Text)
    window_size = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'user_agent': self.user_agent,
            'window_size': self.window_size,
        }
