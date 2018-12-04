from closeio.utils import paginate_via_cursor


def test_paginate_via_cursor():
    responses = {
        '': {'cursor_next': '11111', 'data': [{'id': 1}, {'id': 2}]},
        '11111': {'cursor_next': '22222', 'data': [{'id': 3}, {'id': 4}]},
        '22222': {'cursor_next': '', 'data': [{'id': 5}, {'id': 6}]}
    }

    def test_function(**kwargs):
        cursor = kwargs.get('_cursor')
        return responses[cursor]

    response = paginate_via_cursor(test_function)
    assert list(response) == [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}, {'id': 6}]
