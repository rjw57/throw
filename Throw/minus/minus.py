import httplib
import urllib
import urllib2
import cookielib
import mimetypes
import json


class User(object):
    def __init__(self, username, password1=None):
        self.username = username
        self.password1 = password1

    def SignIn(self):
        """Signs in the User.
        User.password1 attribute must be set to the passsword before calling this method.
        Otherwise, an Exception will be raised."""
        if not self.password1:
            raise Exception("There is no password set. Set the User.password1 attribute to the password before calling this method.")
        else:
            url = "http://min.us/api/SignIn"
            params = {"username":self.username, "password1":self.password1}

            self.cj = cookielib.CookieJar()
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
            self.login_data = urllib.urlencode(params)
            reponse = self.opener.open(url, self.login_data)
            
            parsed = json.loads(reponse.readlines()[0])
            if parsed["success"] == False:
                raise Exception("Sign in failed.")
            return parsed


    def SignOut(self):
        """Signs the User out of min.us."""
        url = "http://min.us/api/SignOut"
        response = self.opener.open(url)

    def MyGalleries(self, returnObject=False):
        """Returns a list of Gallery objects if returnObject=True.
        If returnObject=False, it will return the parsed response
        from the server as a dict.

        Both the Gallery and dict contain the same information,
        but both are availble for diversity.

        NOTE: If the editor_id is not available, it is set to 'Unavailable'
              because that's what the API json value is."""

        # TODO
        # Check if the API returns Unavailable for the editor_id
        

        url = "http://min.us/api/MyGalleries.json"

        response = self.opener.open(url)
        parsed = _parseResponse  

        if returnObject == True:
            galleryList = []
            for gallery in parsed["galleries"]:
                galleryList.append(Gallery(gallery["reader_id"], editor_id=gallery["editor_id"], \
                                           name=gallery["name"], last_visit=gallery["last_visit"], \
                                           item_count=gallery["item_count"], \
                                           clicks=gallery["clicks"]))
        elif returnObject == False:
            return parsed

    def Galleries(self):
        """To be used in the future if other users' Galleries are available through the API.
        
        This method currently does nothing."""
        pass

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
    """Creates a Gallery on the server. Returns a Gallery object with the editor_id and reader_id."""
    url = 'http://min.us/api/CreateGallery'

    response = _dopost(url)

    _editor_id = response["editor_id"]
    _reader_id = response["reader_id"]
    
    return Gallery(_reader_id, editor_id=_editor_id)
    

def UploadItem(filename, gallery, desiredName=None):
    """filename is the full file location and name of the file
    WARNING: If your desiredName doesn't have a proper file extension (SHOULD be the same as the filename)
             it'll still upload, but you won't be able to download it or view it online.
             You can edit the name later to add the extension, but be careful, because it seems like you
             can't change the extension after that."""

    url = 'http://min.us/api/UploadItem?'   # Must have the ? because urlencode doesn't add that on itself

    if desiredName:
        name = desiredName
    else:
        name = filename

    params = {"editor_id":gallery.editor_id, "filename":name}
    
    with file(filename, 'rb') as f:
        itemData = f.read()
        
    response = _dopost(url, params=params, payload=itemData)

    _id = response["id"]
    _height = response["height"]
    _width = response["width"]
    _filesize = response["filesize"]

    return Item(_id, height=_height, width=_width, filesize=_filesize)    

def _doget(url):
    response = urllib2.urlopen(url)
    return _parseResponse(response)


def _dopost(url, params=None, payload=None):
    if params:
        encoded = urllib.urlencode(params)
    else:
        encoded = ''

    url = str(url + encoded)

    if payload is None:
        payload = ''

    response = urllib2.urlopen(url, payload)

    return _parseResponse(response) 

def _parseResponse(response):
    return json.loads(''.join(response.readlines()))    # response.readlines() is a list of many parts of the json.

