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

from terminalinterface import *
import identity

import minus.minus as minus

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

        outer = MIMEMultipart()
        if name is None:
            outer['Subject'] = 'Files thrown at you'
        else:
            outer['Subject'] = 'Files thrown at you: %s' % (name,)
        outer['From'] = self._identity.get_rfc2822_address()
        outer['To'] = ', '.join(to)
        outer.preamble = 'Here are some files for you'

        if(total_size < Thrower.MAX_EMAIL_SIZE):
            # Less than the maximum email size, email directly
            self._attach_files(outer, filepaths, name)
        else:
            self._share_files(outer, filepaths, name)

        self._identity.sendmail(to, outer.as_string())

    def _share_files(self, outer, filepaths, name):
        gallery = minus.CreateGallery()

        if name is not None:
            gallery.SaveGallery(name)

        self._interface.new_section()
        self._interface.message(\
            'Uploading files to http://min.us/m%s...' % (gallery.reader_id,))

        item_map = { }
        for path in filepaths:
            self._interface.message('Uploading %s...' % (os.path.basename(path),))
            self._interface.start_progress()
            item = minus.UploadItem(path, gallery,
                    os.path.basename(path), self._interface.update_progress)
            self._interface.end_progress()
            item_map[item.id] = os.path.basename(path)

        msg_str = ''
        msg_str += "I've shared some files with you. They are viewable as a "
        msg_str += "gallery at the following link:\n\n - http://min.us/m%s\n\n" %\
                (gallery.reader_id,)
        msg_str += "The individual files can be downloaded from the following "
        msg_str += "links:\n\n"

        for item, name in item_map.items():
            msg_str += ' - http://i.min.us/j%s%s %s\n' % \
                    (item, os.path.splitext(name)[1], name)

        msg = MIMEText(msg_str)
        msg.add_header('Format', 'Flowed')
        outer.attach(msg)

    def _attach_files(self, outer, filepaths, name):
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

            if maintype == 'image':
                fp = open(path, 'rb')
                msg = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(path, 'rb')
                msg = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'text':
                # We do this to catch cases where text files have
                # an encoding we can't guess correctly.
                try:
                    fp = open(path, 'r')
                    msg = MIMEText(fp.read(), _subtype=subtype)
                    fp.close()
                except UnicodeDecodeError:
                    fp = open(path, 'rb')
                    msg = MIMEBase(maintype, subtype)
                    msg.set_payload(fp.read())
                    encoders.encode_base64(msg)
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

        outer.attach(MIMEText("Here are some files I've thrown at you."))
        
        for path in filepaths:
            self._interface.literal_message('.')
            add_file_to_outer(path)

