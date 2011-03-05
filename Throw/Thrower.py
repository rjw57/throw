import logging
import Throw.TerminalInterface as TerminalInterface
import Throw.Config as cfg

def throw(to, paths):
    t = Thrower()
    t.throw(to, paths)

class Thrower(object):
    log = logging.getLogger('Thrower')

    def __init__(self):
        self._interface = TerminalInterface.TerminalInterface()
        self._config = cfg.Config()

    def throw(self, to, paths):
        if to is None or len(to) == 0:
            self._interface.new_section()

            to = [ ]

            # We need to get some recipients
            self._interface.message("""
            Before I can throw your files at a recipient, I need to know where
            to send them.
            
            I'm going to ask you for a list of recipients. I'll keep going
            until you stop giving me e-mail addresses by just pressing 'enter'
            at the prompt.""")

            while len(to) == 0:
                should_continue = True
                while should_continue:
                    to.append(self._interface.input('E-mail address to send files to'))
                    should_continue = (len(to[-1]) > 0)
                to = to[:-1]

                if len(to) == 0:
                    self._interface.error("You need to give me at least one recipient.")

        identity = {
            'name': self._config.get('user', 'name'),
            'email': self._config.get('user', 'email'),
        }

        ask_to_save = False
        
        if identity['name'] is None:
            self._interface.new_section()
            self._interface.message("""
            I'm going to send your file by email but before I do that, I need 
            to know your name.""")
            identity['name'] = self._interface.input('Your name')
            ask_to_save = True

        if identity['email'] is None:
            self._interface.new_section()
            self._interface.message("""
            I'm going to send your file by email but before I do that, I need 
            to know your e-mail address.""")
            identity['email'] = self._interface.input('Your e-mail address')
            ask_to_save = True
        
        if ask_to_save:
            self._interface.new_section()
            self._interface.message("""
            Would you like me to remember your answers for next time? You can
            change the name and email address I use to send email later.""")
            should_save = self._interface.input_boolean('Rememeber these values')

            if should_save:
                self._config.set('user', 'name', identity['name'])
                self._config.set('user', 'email', identity['email'])

