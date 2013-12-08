#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import getpass
import logging
import os
import sys

from utils import HelpFormatter, netrc_credentials
import _version


def parse_args():
    """Parse the command line arguments/options.
    """

    parser = argparse.ArgumentParser(
        prog='coursera-dl',
        description="""Coursera-dl is a python package for downloading
        course videos and resources available at coursera.org.
        """,
        add_help=False,
        formatter_class=HelpFormatter)

    positional = parser.add_argument_group('Positional arguments')
    general = parser.add_argument_group('General options')
    authentication = parser.add_argument_group('Authentication options')
    filter = parser.add_argument_group('Filter options')
    filesystem = parser.add_argument_group('Filesystem options')
    download = parser.add_argument_group('Download options')
    debugging = parser.add_argument_group('Debugging / Verbosity options')

    # Positional argument
    positional.add_argument('course',
                            nargs='*',
                            help="""one or more courses to download, use the
                                 identifier from the course URL:
                                 https://class.coursera.org/<course>""")

    # General Options
    general.add_argument('-h',
                         '--help',
                         action='help',
                         help='show this help message and exit')
    general.add_argument('--version',
                         action='version',
                         version=_version.__version__)
    general.add_argument('--preview',
                         dest='preview',
                         action='store_true',
                         default=False,
                         help='download preview videos instead'
                              ' of the regular course material')
    general.add_argument('--download-about',
                         dest='about',
                         action='store_true',
                         default=False,
                         help='additionally download about metadata to'
                              ' about.json')
    general.add_argument('-r',
                         '--reverse',
                         dest='reverse',
                         action='store_true',
                         default=False,
                         help='download and save sections in reverse order')
    general.add_argument('--parser',
                         dest='parser',
                         type=str,
                         default='html5lib',
                         help='html parser to use, one of [html5lib'
                              ' html.parser lxml] (default: html5lib)')
    general.add_argument('--proxy',
                         dest='proxy',
                         metavar='URL',
                         default=None,
                         help='use the specified HTTP/HTTPS proxy')
    general.add_argument('--hooks',
                         dest='hooks',
                         action='append',
                         default=[],
                         help='hooks to run when finished')
    general.add_argument('--playlist',
                         dest='playlist',
                         action='store_true',
                         default=False,
                         help='generate M3U playlist for every course section')

    # Authentication Options
    authentication.add_argument('-u',
                                '--username',
                                dest='username',
                                action='store',
                                default=None,
                                help='coursera username')
    authentication.add_argument('-p',
                                '--password',
                                dest='password',
                                action='store',
                                default=None,
                                help='coursera password')
    authentication.add_argument('-n',
                                '--netrc',
                                metavar='FILE',
                                dest='netrc',
                                nargs='?',
                                action='store',
                                const=True,
                                default=None,
                                help='use netrc for reading passwords, uses '
                                     'default location if no file specified')

    # Filtering Options
    filter.add_argument('--sections',
                        metavar='NUMBERS',
                        dest='sections',
                        default='',
                        help='space separated list of section numbers'
                             ' to download, e.g. "1 3 8"')
    filter.add_argument('-f',
                        '--formats',
                        metavar='EXTENSIONS',
                        dest='formats',
                        action='store',
                        default='',
                        help='space separated list of file extensions'
                             ' to download, e.g "mp4 pdf"')
    filter.add_argument('--skip-formats',
                        dest='skip_formats',
                        metavar='EXTENSIONS',
                        default='',
                        help='space separated list of file extensions to skip,'
                             ' e.g., "ppt srt pdf"')
    filter.add_argument('-sf',
                        '--section-filter',
                        metavar='REGEX',
                        dest='section_filter',
                        action='store',
                        default=None,
                        help='only download sections which contain this'
                             ' regex (default: disabled)')
    filter.add_argument('-lf',
                        '--lecture-filter',
                        metavar='REGEX',
                        dest='lecture_filter',
                        action='store',
                        default=None,
                        help='only download lectures which contain this regex'
                             ' (default: disabled)')
    filter.add_argument('-rf',
                        '--resource-filter',
                        metavar='REGEX',
                        dest='resource_filter',
                        action='store',
                        default=None,
                        help='only download resources which match this regex'
                             ' (default: disabled)')

    # Filesystem Options
    filesystem.add_argument('-d',
                            '--destination',
                            metavar='DIR',
                            dest='destination',
                            type=str,
                            default=".",
                            help='location in filesystem where everything'
                                 ' will be saved')
    filesystem.add_argument('-o',
                            '--output',
                            metavar='TEMPLATE',
                            dest='output',
                            type=str,
                            default=".",
                            help='output filename template')
    filesystem.add_argument('--archive',
                            dest='archive',
                            action='store_true',
                            default=False,
                            help='tarball courses for archival storage')
    filesystem.add_argument('--overwrite',
                            dest='overwrite',
                            action='store_true',
                            default=False,
                            help='overwrite already downloaded files')
    filesystem.add_argument('--max-filename-length',
                            metavar="NUMBER",
                            dest='max_filename_length',
                            type=int,
                            default=100,
                            help='maximum length of filenames/directories'
                                 ' in a path (windows only)')

    # Download Options
    download.add_argument('--wget',
                          metavar='BIN',
                          dest='wget',
                          action='store',
                          nargs='?',
                          const='wget',
                          default=None,
                          help='download using wget')
    download.add_argument('--curl',
                          metavar='BIN',
                          dest='curl',
                          action='store',
                          nargs='?',
                          const='curl',
                          default=None,
                          help='download using curl')
    download.add_argument('--aria2',
                          metavar='BIN',
                          dest='aria2',
                          action='store',
                          nargs='?',
                          const='aria2c',
                          default=None,
                          help='download using aria2')
    download.add_argument('--axel',
                          metavar='BIN',
                          dest='axel',
                          action='store',
                          nargs='?',
                          const='axel',
                          default=None,
                          help='download using axel')

    # Debugging Options
    debugging.add_argument('--cookies',
                           dest='cookies',
                           action='store',
                           default=None,
                           help='file to read cookies from')
    debugging.add_argument('--lectures-page',
                           metavar='FILE',
                           dest='lectures_page',
                           help='uses/creates local cached version of'
                                ' syllabus lectures page')
    debugging.add_argument('--skip-download',
                           dest='skip_download',
                           action='store_true',
                           default=False,
                           help='do not download files')
    debugging.add_argument('-s',
                           '--simulate',
                           dest='simulate',
                           action='store_true',
                           default=False,
                           help='do not download the files and'
                                ' do not write anything to disk')
    debugging.add_argument('--debug',
                           dest='debug',
                           action='store_true',
                           default=False,
                           help='print lots of debug information')
    debugging.add_argument('--quiet',
                           dest='quiet',
                           action='store_true',
                           default=False,
                           help='omit as many messages as possible'
                                ' (only printing errors)')
    debugging.add_argument('--cache-dir',
                           metavar='DIR',
                           dest='cache_dir',
                           action='store',
                           default=None,
                           help="""location in the filesystem where %(prog)s
                                can store downloaded information permanently,
                                the default location is /tmp""")
    debugging.add_argument('--no-cache-dir',
                           dest='no_cache_dir',
                           action='store_true',
                           default=False,
                           help='disable filesystem caching')
    debugging.add_argument('--clear-cache',
                           dest='clear_cache',
                           action='store_true',
                           default=False,
                           help='clear cached cookies')

    return parser.parse_args()


def validate_args(args):
    """Validate and sanitize the command line arguments/options, fail fast.
    """

    # Check the parser
    if args.parser == "html.parser" and sys.version_info < (2, 7, 3):
        logging.info("Warning: 'html.parser' may cause problems"
                     " on Python < 2.7.3")
    if args.parser not in ['html5lib', 'html.parser', 'lxml']:
        logging.error("Invalid parser: '%s',"
                      " choose from 'html5lib', 'html.parser', 'lxml'",
                      args.parser)
        sys.exit(1)

    # Check if sections is a list of integers
    try:
        args.sections = [int(x) for x in args.sections.split()]
    except Exception as e:
        logging.error("Invalid sections list, this should be a"
                      " list of integers.")
        sys.exit(1)

    # Split string of extensions, remove prefixing dot if there is one
    args.formats = [s.lstrip('.') for s in args.formats.split()]
    args.skip_formats = [s.lstrip('.') for s in args.skip_formats.split()]

    # We do not need the username/password if a cookies file is specified
    if args.cookies:
        if not os.path.exists(args.cookies):
            logging.error("Cookies file not found: %s", args.cookies)
            sys.exit(1)
    else:
        if args.netrc:
            credentials = netrc_credentials(
                None if args.netrc is True else args.netrc)
            if credentials is None:
                logging.error("No credentials found in .netrc file")
                sys.exit(1)
            logging.info("Credentials found in .netrc file")
            args.username = credentials[0]
            args.password = credentials[1]
        else:
            if not args.username:
                logging.error('Please provide a username with the -u option, '
                              'or a .netrc file with the -n option.')
                sys.exit(1)
            if not args.password:
                args.password = getpass.getpass(
                    'Coursera password for {0}: '.format(args.username))

    return args


def main():
    args = parse_args()

    # Initialize the logging system first so that other functions
    # can use it right away
    if args.debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(name)s[%(funcName)s] %(message)s')
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR,
                            format='%(name)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(message)s')

    args = validate_args(args)

    logging.info("Coursera-dl v%s (%s)" % (_version.__version__, args.parser))


if __name__ == '__main__':
    main()
