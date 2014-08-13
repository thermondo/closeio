import random

import pytest


@pytest.fixture
def random_string():
    return '%030x' % random.randrange(16 ** 30)


@pytest.yield_fixture
def lead_status(closeio, random_string):
    ls = closeio.create_lead_status(random_string)

    yield ls

    # closeio.delete_lead_status(ls['id'])


@pytest.yield_fixture
def opportunity_status(closeio, random_string):
    os = closeio.create_opportunity_status(random_string, 'active')

    yield os

    # closeio.delete_lead_status(ls['id'])
