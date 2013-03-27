"""
The following is the Google App Engine loader for pytz.

It is monkeypatched, prepending pytz/__init__.py

Here are some helpful links discussing the problem:

    https://code.google.com/p/gae-pytz/source/browse/pytz/gae.py
    http://appengine-cookbook.appspot.com/recipe/caching-pytz-helper/

This is all based on the helpful gae-pytz project, here:

    https://code.google.com/p/gae-pytz/
"""
import logging

# easy test to make sure we are running the appengine version
APPENGINE_PYTZ = True

# Put pytz into its own ndb namespace, so we avoid conflicts
NDB_NAMESPACE = '.pytz'

# True when we are running on google app engine; otherwise pytz reverts
# to the original open_resource/resource_exists
is_gae = True

# This is enabled when a unit test runner calls setup_module
_appengine_testbed = False

try:
    from google.appengine.ext import ndb
except ImportError as ie:
    is_gae = False

def _is_gae_test():
    """Returns true if pytz thinks we are running on Google App Engine,
    Google App Engine's development server"""
    import os
    server_software = os.environ.get('SERVER_SOFTWARE', '')
    return (server_software.startswith('Google App Engine') or
            server_software.startswith('Development'))

# If we are running Google App Engine, use our resource loader, otherwise
# fall back to the original
is_gae = _is_gae_test()

class Zoneinfo(ndb.Model):
    """A model containing the zone info data
    """
    data = ndb.BlobProperty(compressed=True)

def init_zoneinfo():
    """
    Add each zone info to the datastore. This will overwrite existing zones.

    This must be called before the AppengineTimezoneLoader will work.
    """
    import os
    from zipfile import ZipFile
    zoneobjs = []

    zoneinfo_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
      'zoneinfo.zip'))

    with ZipFile(zoneinfo_path) as zf:
        for zfi in zf.filelist:
            key = ndb.Key('Zoneinfo', zfi.filename, namespace=NDB_NAMESPACE)
            zobj = Zoneinfo(key=key, data=zf.read(zfi))
            zoneobjs.append(zobj)

    logging.info("Adding %d timezones to the pytz-appengine database" %
        len(zoneobjs)
        )

    ndb.put_multi(zoneobjs)

def open_resource(name):
    """Load the object from the datastore"""
    from cStringIO import StringIO
    global is_gae
    logging.error("Opening %s, gae: %s" % (name, is_gae))
    raise Exception("WTFA")

    if not is_gae:
        # fallback to original
        return __open_resource(name)

    try:
        data = ndb.Key('Zoneinfo', name, namespace=NDB_NAMESPACE).get().data
    except AttributeError:
        # Missing zone info; test for GMT - which would be there if the 
        # Zoneinfo has been initialized.
        if ndb.Key('Zoneinfo', 'GMT', namespace=NDB_NAMESPACE).get():
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
    global is_gae
    if is_gae: return True

    # fallback to original
    return __resource_exists(name)

def setup_module():
    """Set up tests (used by e.g. nosetests) for the module - loaded once"""
    from google.appengine.ext import testbed
    global _appengine_testbed
    global is_gae
    tb = testbed.Testbed()
    tb.activate()
    tb.setup_env()
    tb.init_datastore_v3_stub()
    tb.init_memcache_stub()

    _appengine_testbed = tb
    is_gae = True

def teardown_module():
    """Any clean-up after each test"""
    global _appengine_testbed
    _appengine_testbed.deactivate()

#
# >>>>>>>>>>>>>
# >>>>>>>>>>>>>     end pytz-appengine augmentation
# >>>>>>>>>>>>>
#
# The following shall be the canonical pytz/__init__.py, modified to change 
# open_resource and resource_exists
#
