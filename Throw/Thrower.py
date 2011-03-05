import logging
import smtplib
import os
import mimetypes

from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

        if identity['name'] is None or identity['email'] is None:
            self._interface.new_section()
            self._interface.message("""
            I'm going to send your file by email but before I do that, I need 
            to know your name and email address""")

            if identity['name'] is None:
                identity['name'] = self._interface.input('Your name')

            if identity['email'] is None:
                identity['email'] = self._interface.input('Your e-mail address')

            self._interface.message("""
            Would you like me to remember your answers for next time? You can
            change the name and email address I use to send email later.""")
            if self._interface.input_boolean('Rememeber these values'):
                self._config.set('user', 'name', identity['name'])
                self._config.set('user', 'email', identity['email'])

        outer = MIMEMultipart()
        outer['Subject'] = 'Files thrown at you'
        outer['From'] = '%s <%s>' % (identity['name'], identity['email'])
        outer['To'] = ', '.join(to)
        outer.preamble = 'Here are some files for you'

        def add_file_to_outer(path):
            if not os.path.isfile(path):
                return

            # Guess the content type based on the file's extension.  Encoding
            # will be ignored, although we should check for simple things like
            # gzip'd or compressed files.
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            #if maintype == 'text':
            #    fp = open(path)
            #    msg = MIMEText(fp.read(), _subtype=subtype)
            #    fp.close()
            if maintype == 'image':
                fp = open(path, 'rb')
                msg = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(path, 'rb')
                msg = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(path, 'rb')
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                encoders.encode_base64(msg)

            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment',
                    filename=os.path.basename(path))
            outer.attach(msg)

        def add_dir_to_outer(dirpath):
            if not os.path.isdir(dirpath):
                return

            add_paths_to_outer(\
                    [os.path.join(dirpath, x) for x in os.listdir(dirpath)])

        def add_paths_to_outer(paths):
            for path in paths:
                if os.path.isfile(path):
                    add_file_to_outer(path)
                elif os.path.isdir(path):
                    add_dir_to_outer(path)

        add_paths_to_outer(paths)

        print(outer.as_string())

        #server = smtplib.SMTP_SSL('localhost')
        #server.sendmail(msg['From'], to, msg.as_string())
        #server.quit()

