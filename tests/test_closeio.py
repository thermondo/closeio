"""
test_closeio
----------------------------------

Tests for `closeio` module.
"""
import datetime
import types
import unittest

from dateutil.tz import tzutc

from closeio.utils import convert, parse

LEAD = {
    "status_id": "stat_1ZdiZqcSIkoGVnNOyxiEY58eTGQmFNG3LPlEVQ4V7Nk",
    "status_label": "Potential",
    "tasks": [],
    "display_name": "Wayne Enterprises (Sample Lead)",
    "addresses": [],
    "contacts": [
        {
            "name": "Bruce Wayne",
            "title": "The Dark Knight",
            "date_updated": "2013-02-06T20:53:01.954000+00:00",
            "phones": [
                {
                    "phone": "+1234",
                    "phone_formatted": "+1 234",
                    "type": "office"
                }
            ],
            "created_by": None,
            "id": "cont_o0kP3Nqyq0wxr5DLWIEm8mVr6ZpI0AhonKLDG0V5Qjh",
            "organization_id": "orga_bwwWG475zqWiQGur0thQshwVXo8rIYecQHDWFanqhen",
            "date_created": "2013-02-01T00:54:51.331000+00:00",
            "emails": [
                {
                    "type": "office",
                    "email_lower": "thedarkknight@close.io",
                    "email": "thedarkknight@close.io"
                }
            ],
            "updated_by": "user_04EJPREurd0b3KDozVFqXSRbt2uBjw3QfeYa7ZaGTwI"
        }
    ],
    "date_updated": "2013-02-06T20:53:01.977000+00:00",
    "description": "",
    "html_url": "https://app.close.io/lead/lead_IIDHIStmFcFQZZP0BRe99V1MCoXWz2PGCm6EDmR9v2O/",
    "created_by": None,
    "custom": {
        "time_of_death": "01:00:00",
        "date_of_death": "1988-11-19",
        "foo": "bar"
    },
    "organization_id": "orga_bwwWG475zqWiQGur0thQshwVXo8rIYecQHDWFanqhen",
    "url": None,
    "opportunities": [
        {
            "status_id": "stat_4ZdiZqcSIkoGVnNOyxiEY58eTGQmFNG3LPlEVQ4V7Nk",
            "status_label": "Active",
            "status_type": "active",
            "date_won": None,
            "confidence": 75,
            "user_id": "user_scOgjLAQD6aBSJYBVhIeNr6FJDp8iDTug8Mv6VqYoFn",
            "contact_id": None,
            "updated_by": None,
            "date_updated": "2013-02-01T00:54:51.337000+00:00",
            "value_period": "one_time",
            "created_by": None,
            "note": "Bruce needs new software for the Bat Cave.",
            "value": 50000,
            "lead_name": "Wayne Enterprises (Sample Lead)",
            "organization_id": "orga_bwwWG475zqWiQGur0thQshwVXo8rIYecQHDWFanqhen",
            "date_created": "2013-02-01T00:54:51.337000+00:00",
            "user_name": "P F",
            "id": "oppo_8eB77gAdf8FMy6GsNHEy84f7uoeEWv55slvUjKQZpJt",
            "lead_id": "lead_IIDHIStmFcFQZZP0BRe99V1MCoXWz2PGCm6EDmR9v2O"
        }
    ],
    "updated_by": "user_04EJPREurd0b3KDozVFqXSRbt2uBjw3QfeYa7ZaGTwI",
    "date_created": "2013-02-01T00:54:51.333000+00:00",
    "id": "lead_IIDHIStmFcFQZZP0BRe99V1MCoXWz2PGCm6EDmR9v2O",
    "name": "Wayne Enterprises (Sample Lead)"
}


class TestCloseio(unittest.TestCase):
    def setUp(self):
        pass

    def test_something(self):
        pass

    def tearDown(self):
        pass

    def test_parse(self):
        """
        Tests parsing for datetime from JSON string.
        """
        parsed_items = parse(LEAD)
        self.assertEqual(parsed_items["date_updated"],
                         datetime.datetime(2013, 2, 6, 20, 53, 1, 977000, tzinfo=tzutc()))
        self.assertEqual(parsed_items["custom"]["time_of_death"], datetime.time(1))
        self.assertEqual(parsed_items["custom"]["date_of_death"], datetime.date(1988, 11, 19))
        self.assertEqual(parsed_items["custom"]["foo"], "bar")
        p_gen = parse(x for x in range(10))
        is_gen = (x for x in range(10))
        self.assertIsNot(parse(is_gen), is_gen)
        self.assertEqual(list(p_gen), [x for x in range(10)])
        self.assertIsInstance(p_gen, types.GeneratorType)

    def test_convert_full(self):
        assert LEAD == convert(parse(LEAD))

    def test_none(self):
        assert None is convert(None)


if __name__ == '__main__':
    unittest.main()
