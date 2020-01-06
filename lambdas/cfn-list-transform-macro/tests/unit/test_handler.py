import json
import unittest
from list_transform.app import handler


class test_app(unittest.TestCase):

  def test_prepend(self):
    with open(r'events/list_transform_prepend.json') as file:
      test_template = json.load(file)
    self.event = test_template
    result = handler(self.event, None)
    fragment = result['fragment']
    expected = ['FooAlpha', 'FooBeta', 'FooGamma']
    self.assertEqual(expected, fragment)


  def test_append(self):
    with open(r'events/list_transform_append.json') as file:
      test_template = json.load(file)
    self.event = test_template
    result = handler(self.event, None)
    fragment = result['fragment']
    expected = ['AlphaFoo', 'BetaFoo', 'GammaFoo']
    self.assertEqual(expected, fragment)


  def test_missing_prepend(self):
    with open(r'events/list_transform_append.json') as file:
      test_template = json.load(file)
    self.event = test_template
    result = handler(self.event, None)
    fragment = result['fragment']
    expected = ['AlphaFoo', 'BetaFoo', 'GammaFoo']
    self.assertEqual(expected, fragment)
