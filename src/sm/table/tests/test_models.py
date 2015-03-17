from ..models import Table


class TestTable(object):

    def test_to_dict(self):
        """
        .to_dict should return dict representation of Table object.
        """
        obj = Table(
            id=10,
            timestamp='timestamp1',
            user_agent='user agent2',
            window_size='window size3'
        )

        assert obj.to_dict() == {
            'id': 10,
            'timestamp': 'timestamp1',
            'user_agent': 'user agent2',
            'window_size': 'window size3',
        }
