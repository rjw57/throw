"""min.us support module.

This code is based on the code from http://code.google.com/p/python-minus/ but
has been modified to be Python3 friendly and, where it is available, to make
use of the pycurl module.

We don't make use of the user login feature of min.us and so that code has been
stripped out to make maintainance easier.

"""

import mimetypes
import json

# Try to import PyCURL if we have it but silently swallow the exception if it
# isn't available (such as with Python3...).
try:
    import pycurl
except ImportError:
    pass

# This magic is to support the module re-naming that happened with the Python
# 2->3 transition.
try:
    from urllib import urlencode
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import urlencode

class Gallery(object):
    """Represents a min.us Gallery"""
    def __init__(self, reader_id, editor_id=None, name=None, last_visit=None, \
                 item_count=None, clicks=None):
        self.editor_id = editor_id
        self.reader_id = reader_id
        self.name = name

        # attributes to be used by the User.MyGalleries() method
        self.last_visit = last_visit
        self.item_count = item_count
        self.clicks = clicks

        # items is a list of direct links to multiple items in the gallery.
        # Use GetItems() to update this attribute.
        self.items = None

    def GetItems(self):
        """Updates self.name and self.items and returns (self.name, self.items)"""
        url = 'http://min.us/api/GetItems/' + 'm' + self.reader_id
        response = _doget(url)

        self.name = response["GALLERY_TITLE"]

        # To get the item id, we have to take the file name from the URL
        # We also need to get rid of any file extension if there is any
        self.items = [a[16:].split('.')[0] for a in response["ITEMS_GALLERY"]]

        return (self.name, self.items)


    def SaveGallery(self, name=None, items=None):
        """Use this to update the gallery name or change sort order.
        Specify which attribute (name or items or both) you want to change."""

        url = 'http://min.us/api/SaveGallery'

        if not name:
            if not self.name:
                name = self.GetItems()[0]
            if self.name:
                name = self.name

        if not items:
            if not self.items:
                items = self.GetItems()[1]
            elif self.items:
                items = self.items

        params = {"name": name, "id":self.editor_id, "items":items}

        try:
            response = _dopost(url, params)
        except:
            pass
        else:
            self.name = name
            self.items = items




class Item(object):
    """Represents a min.us item."""
    def __init__(self, id, height=None, width=None, filesize=None):
        self.id = id
        self.height = height
        self.width = width
        self.filesize = filesize


def CreateGallery():
    """Creates a Gallery on the server. Returns a Gallery object with the
    editor_id and reader_id.

    """
    url = 'http://min.us/api/CreateGallery'

    response = _dopost(url)

    _editor_id = response["editor_id"]
    _reader_id = response["reader_id"]

    return Gallery(_reader_id, editor_id=_editor_id)


def UploadItem(filename, gallery, desiredName=None, progress_cb=None):
    """filename is the full file location and name of the file
    WARNING: If your desiredName doesn't have a proper file extension (SHOULD
    be the same as the filename) it'll still upload, but you won't be able to
    download it or view it online. You can edit the name later to add the
    extension, but be careful, because it seems like you can't change the
    extension after that.

    If progress_cb is not None, it should be a callable which takes two
    arguments: the total number of bytes to upload and the number of bytes
    which have been uploaded. The callable is called periodically to show the
    progress of the upload.

    """

    # Must have the ? because urlencode doesn't add that on itself
    url = 'http://min.us/api/UploadItem?'

    if desiredName:
        name = desiredName
    else:
        name = filename

    params = {"editor_id":gallery.editor_id, "filename":name}

    with open(filename, 'rb') as f:
        itemData = f.read()

    response = _dopost(url, params=params,
            payload=itemData, progress_cb=progress_cb)

    _id = response["id"]
    _height = response["height"]
    _width = response["width"]
    _filesize = response["filesize"]

    return Item(_id, height=_height, width=_width, filesize=_filesize)

def _doget(url):
    response = urlopen(url)
    return _parseResponse(response)


def _dopost(url, params=None, payload=None, progress_cb=None):
    """Do a HTTP post to upload some data. If progress_cb is not None, it
    should be a callable which takes two arguments: the total number of bytes
    to upload and the number of bytes which have been uploaded. The callable is
    called periodically to show the progress of the upload.

    """
    if params:
        encoded = urlencode(params)
    else:
        encoded = ''

    url = str(url + encoded)

    if payload is None:
        payload = ''

    # Try to make use of PyCURL if we have it
    try:
        c = pycurl.Curl()
    except NameError:
        c = None

    if c is not None:
        response = [ ]
        def append_to_response(buf):
            response.append(buf.decode())

        def progress(download_t, download_d, upload_t, upload_d):
            if progress_cb is not None:
                progress_cb(upload_d, upload_t)

        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, payload)
        c.setopt(pycurl.INFILESIZE, len(payload))
        c.setopt(pycurl.WRITEFUNCTION, append_to_response)
        c.setopt(pycurl.NOPROGRESS, 0)
        c.setopt(pycurl.PROGRESSFUNCTION, progress)
        c.perform()
        c.close()

        return json.loads(''.join(response))
    else:
        if progress_cb is not None:
            progress_cb(0, len(payload))
        response = [x.decode() for x in urlopen(url, payload).readlines()]
        if progress_cb is not None:
            progress_cb(len(payload), len(payload))
        return json.loads(''.join(response))

def _parseResponse(response):
    # response.readlines() is a list of many parts of the json.
    return json.loads(''.join([x.decode() for x in response.readlines()]))

