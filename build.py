#!/usr/bin/env python
"""
Download and patch the latest version of pytz
"""
import os
import argparse

LATEST_OLSON = "2013b"
#
# TODO: Slurp the latest URL from the pypi downloads page
SRC_TEMPLATE = "https://pypi.python.org/packages/source/p/pytz/pytz-{}.zip"

def download(args):
    "Get the latest pytz"
    import urllib
    source = SRC_TEMPLATE.format(args.olson)
    dest = os.path.basename(source)
    print "Downloading %s" % source

    if os.path.exists(dest):
        print "File %s already exists." % dest
    else:
        urllib.urlretrieve(source, dest)
        print "Download complete."


def compile(args):
    """"Create a 'pytz' directory and create the appengine-compatible module.
    """
    from zipfile import ZipFile

    source = os.path.basename(SRC_TEMPLATE.format(args.olson))
    build_dir = args.build

    # this is what needs to be copied over
    SOURCES = ["pytz/.*\.py", "pytz/zoneinfo"]

    print "Recreating pytz for appengine from %s into %s" % (source, build_dir)

    if not os.path.exists(build_dir):
        os.mkdir(build_dir)

    with ZipFile(source, 'r') as zf:

        # copy the source
        for zip_file_obj in (zfi for zfi in zf.filelist if "/pytz/" in
                zfi.filename and zfi.filename.endswith(".py")):
            out_filename = "%s/%s" % (build_dir,
                    os.path.basename(zip_file_obj.filename))
            with open(out_filename, 'w') as outfile:
                print "Writing %s" % out_filename
                outfile.write(zf.read(zip_file_obj))
        
        # copy the zoneinfo






commands = dict(
        download=download,
        compile=compile,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update the pytz.')

    parser.add_argument('--olson', dest='olson', default=LATEST_OLSON,
            help='The version of the pytz to use')

    parser.add_argument('--build', dest='build', default='pytz',
            help='The build directory where the updated pytz will be stored')

    parser.add_argument('command', help='Action to perform',
            choices=commands.keys())

    args = parser.parse_args()

    command = commands[args.command]
    command(args)
