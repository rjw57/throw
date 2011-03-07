import argparse
import logging

from thrower import *

def main():
    parser = argparse.ArgumentParser(description='Simply share a file.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='*',
        help='the name of a file or directory to share.')
    parser.add_argument('-v', '--verbose', dest='verbose',
        action='store_true',
        help='print verbose loggging information.')
    parser.add_argument('-t', '--to', dest='to', metavar='RECIPIENT', 
        action='append',
        help='a recipient for the file(s).')
    parser.add_argument('-n', '--name', dest='name', metavar='NAME', 
        action='store', default=None,
        help='a descriptive name for this set of files.')

    args = parser.parse_args()

    if(args.verbose):
        logging.basicConfig(level=logging.INFO)

    throw(args.to, args.paths, args.name)

if __name__ == '__main__':
    main()
