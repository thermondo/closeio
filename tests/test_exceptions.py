import pytest

from closeio.exceptions import RateLimitError


class TestExceptions:
    def test_rate_limit_error(self):
        closeio_error_response = {
            'error': {'message': 'API call count exceeded for this period', 'rate_reset': 0.870663,
                      'rate_limit': 40, 'rate_window': 1, 'rate_limit_type': 'key'}
        }
        with pytest.raises(RateLimitError) as exc:
            raise RateLimitError(**closeio_error_response['error'])

        assert exc.value.message is 'API call count exceeded for this period'
