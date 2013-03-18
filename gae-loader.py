"""
The following is the Google App Engine loader for pytz.

It is monkeypatched into pytz/__init__.py

Here are some helpful links discussing the problem:

    https://code.google.com/p/gae-pytz/source/browse/pytz/gae.py
    http://appengine-cookbook.appspot.com/recipe/caching-pytz-helper/

This is all based on the helpful gae-pytz project, here:

    https://code.google.com/p/gae-pytz/
"""

# Put pytz into its own namespace, so we avoid conflicts
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

zoneinfo_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
    'zoneinfo.zip'))

class Zoneinfo(ndb.model):
    """A model containing the zone info data
    """
    data = ndb.BlobProperty(compressed=True)

def init_zoneinfo():
    """
    Add each zone info to the datastore. This will overwrite existing zones.
    """
    from zipfile import ZipFile
    zoneobjs = []

    with namespace_of(NDB_NAMESPACE):
        with open(zoneinfo_path) as zf:
            for zf in zf.filelist:
                key = ndb.Key('Zoneinfo', zf.filename)
                zobj = Zoneinfo(key=key, data=zf.read())
                zoneobjs.append(zobj.put_async())

        ndb.put_multi(zoneobjs)

class TimezoneLoader(object):
    """A loader that that reads timezones using ZipFile."""
    def open_resource(self, name):
        """Load the object from the datastore"""
        from cStringIO import StringIO
        return StringIO(ndb.Key('Zoneinfo', name).get().data)

    def resource_exists(self, name):
        """Return true if the given resource exists"""
        return ndb.Key('Zoneinfo', name).get()

pytz.loader = TimezoneLoader()

