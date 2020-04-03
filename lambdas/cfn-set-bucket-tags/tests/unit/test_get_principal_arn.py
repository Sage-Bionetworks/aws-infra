import unittest

from set_bucket_tags import app


class TestGetPrincipalArn(unittest.TestCase):

  def test_tag_present(self):
    tags = [
      {'Key': 'heresatag', 'Value': 'heresatagvalue'},
      {'Key': 'theresatag', 'Value': 'theresatagvalue'},
      {'Key': 'aws:servicecatalog:provisioningPrincipalArn', 'Value': 'foo'}
    ]
    result = app.get_principal_arn(tags)
    self.assertEqual(result, 'foo')


  def test_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = [
        {'Key': 'heresatag', 'Value': 'heresatagvalue'},
        {'Key': 'theresatag', 'Value': 'theresatagvalue'}
      ]
      app.get_principal_arn(tags)
