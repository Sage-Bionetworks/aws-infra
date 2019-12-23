import json
import jsondiff
import unittest
from explode.app import handler


class test_app(unittest.TestCase):

    def test_no_explode(self):
        event = \
            {
                "requestId": "testRequest",
                "templateParameterValues": {},
                "region": "us-east-1"
            }

        self.event = event

        with open(r'tests/unit/test_no_explode.json') as file:
            test_template = json.load(file)
        self.event["fragment"] = test_template
        result = handler(self.event, None)
        fragment = result["fragment"]

        with open(r'tests/unit/expected_no_explode.json') as file:
            expected_template = json.load(file)

        res = jsondiff.diff(fragment, expected_template)
        self.assertEqual(res, {})

    def test_explode_param(self):
        event = \
            {
                "requestId": "testRequest",
                "templateParameterValues": {
                    "Ports": [22, 80]
                },
                "region": "us-east-1"
            }

        self.event = event

        with open(r'tests/unit/test_explode_param.json') as file:
            test_template = json.load(file)
        self.event["fragment"] = test_template
        result = handler(self.event, None)
        fragment = result["fragment"]

        with open(r'tests/unit/expected_explode_param.json') as file:
            expected_template = json.load(file)

        res = jsondiff.diff(fragment, expected_template)
        self.assertEqual(res, {})

    def test_explode_map(self):
        event = \
            {
                "requestId": "testRequest",
                "templateParameterValues": {},
                "region": "us-east-1"
            }

        self.event = event

        with open(r'tests/unit/test_explode_map.json') as file:
            test_template = json.load(file)
        self.event["fragment"] = test_template
        result = handler(self.event, None)
        fragment = result["fragment"]

        with open(r'tests/unit/expected_explode_map.json') as file:
            expected_template = json.load(file)

        res = jsondiff.diff(fragment, expected_template)
        self.assertEqual(res, {})

    def test_explode_no_match(self):
        event = \
            {
                "requestId": "testRequest",
                "templateParameterValues": {},
                "region": "us-east-1"
            }

        self.event = event

        with open(r'tests/unit/test_explode_no_match.json') as file:
            test_template = json.load(file)
        self.event["fragment"] = test_template
        result = handler(self.event, None)
        fragment = result["fragment"]

        with open(r'tests/unit/expected_explode_no_match.json') as file:
            expected_template = json.load(file)

        res = jsondiff.diff(fragment, expected_template)
        self.assertEqual(res, {})

    def test_explode_map_and_param(self):
        event = \
            {
                "requestId": "testRequest",
                "templateParameterValues": {
                    "Ports": [22, 80]
                },
                "region": "us-east-1"
            }

        self.event = event

        with open(r'tests/unit/test_explode_map_and_param.json') as file:
            test_template = json.load(file)
        self.event["fragment"] = test_template
        result = handler(self.event, None)
        fragment = result["fragment"]

        with open(r'tests/unit/expected_explode_map_and_param.json') as file:
            expected_template = json.load(file)

        res = jsondiff.diff(fragment, expected_template)
        self.assertEqual(res, {})
