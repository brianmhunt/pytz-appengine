#!/usr/bin/env python
"""
Download and patch the latest version of pytz
"""
import os
import os.path
import shutil
import argparse

PYTZ_OUTPUT = 'pytz'

LATEST_OLSON = '2013.8'
#
# TODO: Slurp the latest URL from the pypi downloads page
SRC_TEMPLATE = "https://pypi.python.org/packages/source/p/pytz/pytz-{}.zip"

DONE_TEXT = """

    The `pytz` for Google App Engine has been compiled,
    from: `{source}`

    Testing
    ~~~~~~~

    You can test this with a test-runner such as `nosetests`.
    It is a good idea to set the log-level to INFO or higher
    and turning on color, for example by running:

       $ cd pytz
       $ nosetests --rednose --logging-level=INFO

    Installation
    ~~~~~~~~~~~~

    The appengine-optimized version has been put into `{build_dir}`.

    You can install it by copying `{build_dir}` to your Google App Engine
    project.

    Usage
    ~~~~~

    `pytz` should now work as it always has, but loading the timezones
    from the ndb datastore.

    If you update this package in your Google App Engine installation
    you can refresh the timezones by running `pytz.init_zoneinfo()`
    or alternatively by running in Google App Engine:

       ndb.Key('Zoneinfo', 'GMT', namespace='.pytz').delete()
       pytz.timezone('GMT')

    This will cause the zoneinfo to be refreshed.

    Note that deleted timezones will not be removed from the database
    (but they probably should).
"""


def download(args):
    """Get the latest pytz"""
    import urllib
    if args.release_url:
        source = args.release_url
    else:
        source = SRC_TEMPLATE.format(args.olson)
    dest = os.path.basename(source)
    print "Downloading %s" % source

    if os.path.exists(dest):
        print "File %s already exists." % dest
    else:
        urllib.urlretrieve(source, dest)
        print "Download complete."


def compile(args):
    """Create a 'pytz' directory and create the appengine-compatible module.

    Copy over the bare minimum Python files (pytz/*.py) and put the zonefiles
    into a zip file.
    """
    from zipfile import ZipFile, ZIP_DEFLATED

    if args.release_url:
        source = os.path.basename(args.release_url)
    else:
        source = os.path.basename(SRC_TEMPLATE.format(args.olson))
    build_dir = args.build
    tests_dir = os.path.join(build_dir, 'tests')
    zone_file = os.path.join(build_dir, "zoneinfo.zip")

    print "Recreating pytz for appengine from %s into %s" % (source, build_dir)

    if not os.path.exists(build_dir):
        os.mkdir(build_dir)

    if not os.path.exists(tests_dir):
        os.mkdir(tests_dir)

    with ZipFile(source, 'r') as zf:

        # copy the source
        for zip_file_obj in (
                zfi for zfi in zf.filelist
                if "/pytz/" in zfi.filename
                and zfi.filename.endswith(".py")):
            filename = zip_file_obj.filename  # full path in the zip

            if 'test_' in filename:
                out_filename = '%s/%s' % (
                    tests_dir, os.path.basename(filename))
            else:
                out_filename = "%s/%s" % (
                    build_dir, os.path.basename(filename))

            if not os.path.exists(os.path.dirname(out_filename)):
                os.mkdir(os.path.dirname(out_filename))

            with open(out_filename, 'w') as outfile:
                print "Copying %s" % out_filename
                outfile.write(zf.read(zip_file_obj))

        # copy the zoneinfo to a new zip file
        with ZipFile(zone_file, "w", ZIP_DEFLATED) as out_zones:
            zonefiles = [
                zfi for zfi in zf.filelist
                if "/pytz/zoneinfo" in zfi.filename]
            prefix = os.path.commonprefix([zfi.filename for zfi in zonefiles])
            for zip_file_obj in zonefiles:
                # the destination zip will contain only the contents of the
                # zoneinfo directory e.g.
                # pytz-2013b/pytz/zoneinfo/America/Eastern
                # becoems America/Eastern in our zoneinfo.zip
                out_filename = os.path.relpath(zip_file_obj.filename, prefix)
                # print "Writing %s to %s" % (out_filename, zone_file)
                out_zones.writestr(out_filename, zf.read(zip_file_obj))
            print "Created %s and added %s timezones" % (
                  zone_file, len(zonefiles))

    print "Copying test file test_pytz_appengine.py to %s" % tests_dir
    shutil.copy("test_pytz_appengine.py", tests_dir)

    print "Files copied from %s to the %s directory" % (
          source, build_dir)

    print "Augmenting %s/__init__.py with gae-loader.py" % build_dir

    init_file = os.path.join(build_dir, "__init__.py")
    loader_file = 'gae-loader.py'

    with file(init_file, 'r') as original:
        original_init = original.read()

    # rename open_resource and resource_exists, since we are hacking our own
    original_init = original_init.replace(
        "def open_resource(name):", "def __open_resource(name):")
    original_init = original_init.replace(
        "def resource_exists(name):", "def __resource_exists(name):")

    with open(init_file, "w") as init_out:
        with open(loader_file) as loader_in:
            init_out.write(loader_in.read())

        # append the original __init__
        init_out.write(original_init)

    if args.dir:
        print 'Automatically moving pytz...'

        destination_pytz = os.path.join(args.dir, 'pytz')

        if os.path.isdir(destination_pytz):
            shutil.rmtree(destination_pytz, ignore_errors=True)

        shutil.move('pytz', destination_pytz)

    print DONE_TEXT.format(source=source, build_dir=build_dir)


def clean(args):
    """Erase all the compiled and downloaded documents, being
    pytz/*
    pytz-*
    """
    from glob import glob

    print "Removing pytz- and pytz/*"
    for filename in glob("./pytz-*.zip"):
        print "unlink %s" % filename
        os.unlink(filename)

    for dirname in glob("./pytz-*"):
        print "rmtree %s" % dirname
        shutil.rmtree(dirname)

    print "rmtree %s" % args.build
    shutil.rmtree(args.build)


def all(args):
    """Download and compile."""
    download(args)
    compile(args)


commands = dict(all=all,
                download=download,
                compile=compile,
                clean=clean,
                )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update the pytz.')

    parser.add_argument(
        '--olson', dest='olson', default=LATEST_OLSON,
        help='The version of the pytz to use')

    parser.add_argument(
        '--release-url', dest='release_url',
        help='Explicit pytz release zip URL to download. Overrides --olson')

    parser.add_argument(
        '--dir', dest='dir',
        help='The directory to move the patched pytz to')

    parser.add_argument(
        '--build', dest='build', default=PYTZ_OUTPUT,
        help='The build directory where the updated pytz will be stored')

    parser.add_argument(
        'command', help='Action to perform',
        choices=commands.keys())

    args = parser.parse_args()

    command = commands[args.command]
    command(args)
