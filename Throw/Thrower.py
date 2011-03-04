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
        if to is None or len(to) == 0:
            self._interface.new_section()

        while to is None or len(to) == 0:
            to = [ ]

            # We need to get some recipients
            self._interface.message("""
            Before I can throw your files at a recipient, I need to know where
            to send them.
            
            I'm going to ask you for a list of recipients. I'll keep going
            until you stop giving me e-mail addresses by just pressing 'enter'
            at the prompt.
            
            If you make a mistake, just enter a blank e-mail address since
            I'll ask you in a moment if the list is correct.""")

            should_continue = True
            while should_continue:
                to.append(self._interface.input('E-mail address to send files to'))
                should_continue = (len(to[-1]) > 0)
            to = to[:-1]

            if len(to) == 0:
                self._interface.error("You need to give me at least one recipient.")
                continue

            self._interface.message("""I'm going to send the files to the following email addresses:""")

            self._interface.literal_message('\n'.join([" - " + x for x in to]))

            self._interface.message("""I'll just check with you that you entered all
            the email addresses correctly. If you haven't, I'll ask for them again.""")
            
            if not self._interface.input_boolean("Is this list of e-mail addresses right?"):
                to = None
                
        self._interface.new_section()
        self._interface.message("""
        I'm going to send your file by email but before I do that, I need to know
        your name and the email address you want to send the file from.""")

        identity = { }
        identity['name'] = self._interface.input('Your name')
        identity['email'] = self._interface.input('Your e-mail address')
