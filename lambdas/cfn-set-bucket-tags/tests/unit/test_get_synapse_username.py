import unittest

import requests
import requests_mock

from set_bucket_tags import app


class TestGetSynapseUsername(unittest.TestCase):

  def test_valid_arn(self):
    with requests_mock.Mocker() as m:
      valid_arn = 'arn:aws:sts::237179673806:assumed-role/ServiceCatalogEndusers/3388489'
      url = 'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/3388489'
      m.get(
        url,
        status_code=200,
        text='{"ownerId":"3388489","firstName":"Jane","lastName":"Doe","userName":"janedoe","summary":"","position":"Researcher","location":"Seattle, Washington, USA","industry":"","company":"Sage Bionetworks","url":"","createdOn":"2019-04-16T19:08:04.000Z"}')
      result = app.get_synapse_user_name(valid_arn)
      self.assertEqual(result, 'janedoe')

  def test_invalid_arn(self):
    invalid_arn = 'arn:aws:sts::237179673806:assumed-role/ServiceCatalogEndusers/foobar'
    with self.assertRaises(ValueError):
      app.get_synapse_user_name(invalid_arn)

  def test_valid_not_found_arn(self):
    with requests_mock.Mocker() as m, self.assertRaises(requests.exceptions.HTTPError):
      valid_arn = 'arn:aws:sts::237179673806:assumed-role/ServiceCatalogEndusers/0123456'
      url = 'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/0123456'
      m.get(url, status_code=404, text='{"reason":"UserProfile cannot be found for: 0123456"}')
      app.get_synapse_user_name(valid_arn)
