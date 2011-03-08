import logging
import smtplib
import os

from email import encoders
from email.message import Message
from email.mime.text import MIMEText

from terminalinterface import *
import identity

import emailrenderer.minusgallery
import emailrenderer.attachments

def throw(to, paths, name=None):
    t = Thrower()
    t.throw(to, paths, name=name)

class Thrower(object):
    MAX_EMAIL_SIZE = 500000 # 0.5MB

    log = logging.getLogger('Thrower')

    def __init__(self):
        self._interface = TerminalInterface()
        self._identity = identity.get_default_identity()

    def throw(self, to, paths, name=None):
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
                    to.append(self._interface.input(
                        'E-mail address to send files to'))
                    should_continue = (len(to[-1]) > 0)
                to = to[:-1]

                if len(to) == 0:
                    self._interface.error(
                        'You need to give me at least one recipient.')

        # Get a list of all the individual files to add.
        def append_dir(paths, dirpath):
            contents = [os.path.join(dirpath, x) for x in os.listdir(dirpath)]
            paths += [x for x in contents if os.path.isfile(x)]
            for subdirpath in [x for x in contents if os.path.isdir(x)]:
                append_dir(paths, subdirpath)

        filepaths = []
        filepaths += [x for x in paths if os.path.isfile(x)]
        for dirpath in [x for x in paths if os.path.isdir(x)]:
            append_dir(filepaths, dirpath)

        # Compute the total size of the files
        total_size = 0
        for path in filepaths:
            total_size += os.path.getsize(path)

        self._interface.new_section()
        self._interface.message("""
        You've asked me to throw %s file(s) with a total size of %s MB.""" % \
                (len(filepaths), total_size / 1000000.0))

        if(total_size < Thrower.MAX_EMAIL_SIZE):
            # Less than the maximum email size, email directly
            renderer = emailrenderer.attachments
        else:
            # Use the min.us uploader
            renderer = emailrenderer.minusgallery

        message = renderer.create_email(filepaths, name)
        message['From'] = self._identity.get_rfc2822_address()
        message['To'] = ', '.join(to)

        if name is None:
            message['Subject'] = 'Files thrown at you'
        else:
            message['Subject'] = 'Files thrown at you: %s' % (collection_name,)

        self._identity.sendmail(to, message.as_string())

