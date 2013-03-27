"""
Test the appengine-specific components
"""
import pytz
import logging
import unittest

class pytzAppengineTest(unittest.TestCase):
    """
    Check that loading works as expected and we see the appropriate model
    instances
    """
    def test_pytz_appengine(self):
        "ensure we are using pytz-appengine"
        self.assertTrue(pytz.APPENGINE_PYTZ)

    def test_zones(self):
        """Check that the models do what we expect"""
        from pytz import NDB_NAMESPACE, Zoneinfo
        from google.appengine.ext import ndb

        est = pytz.timezone('Canada/Eastern')
        EXPECT_ZONES = 589 # this may change with each iteration
        zones = Zoneinfo.query(namespace=NDB_NAMESPACE).count()
        self.assertEqual(zones, EXPECT_ZONES)

    def test_is_gae(self):
        """Confirm that pytz will use GAE"""
        import pytz

        self.assertTrue(pytz._is_gae_test())
        self.assertTrue(pytz.is_gae)




