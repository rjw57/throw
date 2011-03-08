import os
import mimetypes

from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_email(filepaths, collection_name):
    """Create an email message object which implements the
    email.message.Message interface and which has the files to be shared
    attached to it.

    """
    outer = MIMEMultipart()
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
        add_file_to_outer(path)

    return outer
