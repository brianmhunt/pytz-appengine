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
        from pytz import NDB_NAMESPACE, Zoneinfo, namespace_of
        from google.appengine.ext import ndb

        est = pytz.timezone('Canada/Eastern')

        logging.error(est)

        EXPECT_ZONES = 589 # this may change with each iteration

        with namespace_of(NDB_NAMESPACE):
            zones = Zoneinfo.query().count()
        
        self.assertEqual(zones, EXPECT_ZONES)

        



