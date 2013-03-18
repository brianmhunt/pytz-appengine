PYTZ - Appengine
================

Python Timezone for appengine.

There are some issues with pytz on appengine, mostly performance related. The
project [gae-pytz](https://code.google.com/p/gae-pytz/) addresses these
performance issues but it has two issues:

1. it not been updated in some time, meaning the timezone data is out of date;
   and
2. it requires importing `pytz.gae` instead of just `pytz`, meaning that any
   existing code (e.g. `icalendar`) must be patched.

This project aims to resolve these issues by automatically building a `pytz` by
downloading the latest version from the launchpad source and building a patched
version.

As well, instead of using the memcache version of gae-pytz, pytz-appengine will
put the timezone information into the datastore with `ndb`.


