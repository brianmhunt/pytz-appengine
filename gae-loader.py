"""
The following is the Google App Engine loader for pytz.

It is monkeypatched, prepending pytz/__init__.py

Here are some helpful links discussing the problem:

    https://code.google.com/p/gae-pytz/source/browse/pytz/gae.py
    http://appengine-cookbook.appspot.com/recipe/caching-pytz-helper/

This is all based on the helpful gae-pytz project, here:

    https://code.google.com/p/gae-pytz/
"""

# easy test to make sure we are running the appengine version
APPENGINE_PYTZ = True

# Put pytz into its own ndb namespace, so we avoid conflicts
NDB_NAMESPACE = '.pytz'

from google.appengine.ext import ndb

# Namespaces
# ~~~~~~~~~~
# Decorator for accessing from within a given namespace
# see eg. http://stackoverflow.com/questions/9296303
from google.appengine.api import namespace_manager

# A context for 'with' 
class namespace_of(object):
    """
    Run the operations in this context in the given namespace
    """
    def __init__(self, namespace):
        self.ns = namespace

    def __enter__(self):
        self.orig_ns = namespace_manager.get_namespace()
        namespace_manager.set_namespace(self.ns)

    def __exit__(self, type, value, traceback):
        namespace_manager.set_namespace(self.orig_ns)


class Zoneinfo(ndb.Model):
    """A model containing the zone info data
    """
    data = ndb.BlobProperty(compressed=True)

def init_zoneinfo():
    """
    Add each zone info to the datastore. This will overwrite existing zones.

    This must be called before the AppengineTimezoneLoader will work.
    """
    import os, logging
    from zipfile import ZipFile
    zoneobjs = []

    zoneinfo_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
      'zoneinfo.zip'))

    with namespace_of(NDB_NAMESPACE):
        with ZipFile(zoneinfo_path) as zf:
            for zfi in zf.filelist:
                key = ndb.Key('Zoneinfo', zfi.filename)
                zobj = Zoneinfo(key=key, data=zf.read(zfi))
                zoneobjs.append(zobj)

        logging.info("Adding %d timezones to the pytz-appengine database" %
            len(zoneobjs)
            )

        ndb.put_multi(zoneobjs)

def open_resource(name):
    """Load the object from the datastore"""
    import logging
    from cStringIO import StringIO
    with namespace_of(NDB_NAMESPACE):
      try:
        data = ndb.Key('Zoneinfo', name).get().data
      except AttributeError:
        # Missing zone info; test for GMT - which would be there if the 
        # Zoneinfo has been initialized.
        if ndb.Key('Zoneinfo', 'GMT').get():
          # the user asked for a zone that doesn't seem to exist.
          logging.exception("Requested zone '%s' is not in the database." %
              name)
          raise

        # we need to initialize the database
        init_zoneinfo()
        return open_resource(name)

    return StringIO(data)

def resource_exists(name):
    """Return true if the given timezone resource exists.
    Since we are loading the whole PyTZ database, this should always be true
    """
    return True

def setup_module():
    """Set up tests (used by e.g. nosetests) for the module - loaded once"""
    from google.appengine.ext import testbed
    global _appengine_testbed
    tb = testbed.Testbed()
    tb.activate()
    tb.setup_env()
    tb.init_datastore_v3_stub()
    tb.init_memcache_stub()

    _appengine_testbed = tb


def teardown_module():
    """Any clean-up after each test"""
    global _appengine_testbed
    _appengine_testbed.deactivate()

#
# >>>>>>>>>>>>>
# >>>>>>>>>>>>>     end pytz-appengine augmentation
# >>>>>>>>>>>>>
#
