import os
from email.mime.text import MIMEText

import minus.minus as minus
from terminalinterface import TerminalInterface

def create_email(filepaths, collection_name):
    """Create an email message object which implements the
    email.message.Message interface and which has the files to be shared
    uploaded to min.us and links placed in the message body.

    """
    gallery = minus.CreateGallery()

    if collection_name is not None:
        gallery.SaveGallery(collection_name)

    interface = TerminalInterface()
    interface.new_section()
    interface.message(\
        'Uploading files to http://min.us/m%s...' % (gallery.reader_id,))

    item_map = { }
    for path in filepaths:
        interface.message('Uploading %s...' % (os.path.basename(path),))
        interface.start_progress()
        item = minus.UploadItem(path, gallery,
                os.path.basename(path), interface.update_progress)
        interface.end_progress()
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
    
    return msg
