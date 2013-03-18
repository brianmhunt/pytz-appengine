"""
Test the appengine-specific components
"""
import pytz

import unittest

class pytzAppengineTest(unittest.TestCase):
    """
    Check that loading works as expected and we see the appropriate model
    instances
    """
    def test_pytz_appengine(self):
        "ensure we are using pytz-appengine"
        self.assertTrue(pytz.APPENGINE_PYTZ)

