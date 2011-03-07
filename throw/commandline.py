"""Implement the command line interface for throw"""

import argparse
import logging
import sys
import os

import terminalinterface
import identity
import thrower

class CommandLine(object):
    def __init__(self):
        self._interface = terminalinterface.TerminalInterface()

        self._parser = argparse.ArgumentParser(description='Simply share a file.')
        self._parser.add_argument('paths', metavar='PATH', type=str, nargs='*',
            help='the name of a file or directory to share.')
        self._parser.add_argument('-v', '--verbose', dest='verbose',
            action='store_true',
            help='print verbose loggging information.')
        self._parser.add_argument('-t', '--to', dest='to', metavar='RECIPIENT', 
            action='append',
            help='a recipient for the file(s).')
        self._parser.add_argument('-n', '--name', dest='name', metavar='NAME', 
            action='store', default=None,
            help='a descriptive name for this set of files.')
        self._parser.add_argument('--set', dest='set', metavar='OPTION',
            help='set a configuration option.',
            choices=('identity',))
        self._parser.add_argument('--test-email', dest='send_test_email',
            action='store_true', help='attempt to send a test email.')

    def main(self, argv):
        args = self._parser.parse_args(argv)

        if args.verbose:
            logging.basicConfig(level=logging.INFO)

        if args.send_test_email:
            try:
                config_id = identity.load_identity()
                config_id.send_test_email()
            except KeyError:
                self._interface.error("""There is no default identity set up.

                You need to run the following command first:

                %s --set identity""" % os.path.basename(sys.argv[0]))

        elif args.set is not None:
            if args.set == 'identity':
                self.set_identity()
        else:
            thrower.throw(args.to, args.paths, args.name)

    def set_identity(self):
        new_identity = identity.input_identity()
        new_identity.save_to_config()
