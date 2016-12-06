PYTZ - Appengine
================

### Note: As of Dec 1, 2016, AppEngine appears to natively include pytz 2016.4.


Python Timezone for Google App Engine.

There are some issues with pytz on Google App Engine, mostly performance related.
The project [gae-pytz](https://code.google.com/p/gae-pytz/) addresses these
performance issues but it has two issues itself:

1. it not been updated in some time, meaning the timezone data is out of date;
   and
2. it requires importing `pytz.gae` instead of just `pytz`, meaning that any
   existing code (e.g. `icalendar`) must be patched.

This project aims to resolve these issues. It automatically builds a `pytz` by
downloading the latest version from the
[launchpad source](https://launchpad.net/pytz) and building a patched version.

Also, instead of using the memcache approach of gae-pytz, pytz-appengine will
put the timezone information into the datastore with `ndb`. This may or may not
confer a performance advantage.

## Installation and usage

To install: clone the repository, then from the command line run

    $ python build.py all

This downloads the latest canonical `pytz` packages from PyPi and augments them
by adding the code necessary to run on Google App Engine.

The build process creates a directory `pytz`, which you can copy to your Google
App Engine directory. This is the augmented pytz module, that ought to work by
storing the timezone information in `ndb`.

I have not created a PyPi package because it doesn't make sense in this
context. One will never import anything directly from this package; it is
essentially just a build script in python.

Thoughts and feedback are welcome.

## License

This project may be copied and otherwise used pursuant to the included MIT
License.
