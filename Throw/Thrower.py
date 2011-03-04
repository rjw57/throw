import logging
import Throw.TerminalInterface as TerminalInterface

def throw(to, paths):
    t = Thrower()
    t.throw(to, paths)

class Thrower(object):
    log = logging.getLogger('Thrower')

    def __init__(self):
        self._interface = TerminalInterface.TerminalInterface()

    def throw(self, to, paths):
        Thrower.log.info('Sending files to %s.' % (to,))
        Thrower.log.info('Sending %s.' % (paths,))

        self._interface.message("""
        I'm going to send your file by email but before I do that, I need to know
        your name and the email address you want to send the file from.""")

        identity = { }
        identity['name'] = self._interface.input('Your name: ')
        identity['email'] = self._interface.input('Your e-mail address: ')
