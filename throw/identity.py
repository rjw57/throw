"""Manage the user's identity."""

import logging
import sys
import os

from email.utils import formataddr
from email.mime.text import MIMEText

from terminalinterface import TerminalInterface
from config import Config

def get_default_identity():
    try:
        return load_identity()
    except KeyError:
        pass

    # Failed ot load identity: input it from the user
    identity = input_identity()
    if self._interface.input_boolean('Save this information for next time?'):
        identity.save_to_config()

    return identity

def load_identity(config = Config()):
    """Load the default identity from the configuration. If there is no default
    identity, a KeyError is raised.
    
    """
    return Identity(name = config.get('user', 'name'),
                    email_ = config.get('user', 'email'))

def input_identity(interface = TerminalInterface()):
    """Get the full name, email address and SMTP information from the user."""

    identity = interface.input_fields("""
       In order to send your files via email, I need to get your name and
       email address you will be using to send the files.""",
       ( 'name', 'Your full name', 'string' ),
       ( 'email', 'Your email address', 'string' ))

    new_identity = Identity(identity['name'], identity['email'])

    # Ask if we want to send a test email.
    if interface.input_boolean('Do you want to try sending a test email to yourself?'):
        message = MIMEText('This is an example email from throw.')
        message['Subject'] = 'A test email from throw'
        message['To'] = new_identity.get_rfc2822_address()
        message['From'] = new_identity.get_rfc2822_address()
        new_identity.sendmail(
            new_identity.get_rfc2822_address(),
            message.as_string())

    return new_identity


class Identity(object):
    """An identity suitable for sending email from. This contains both
    the user's full name, email address and SMTP information."""

    __log = logging.getLogger(__name__ + '.Identity')

    def __init__(self, name, email_):
        """Initialise an identity."""

        self._interface = TerminalInterface()
        self._name = name
        self._email = email_
        Identity.__log.info('Initialised identity "%s".' % self.get_rfc2822_address())
    
    def get_email(self):
        """Return the email address."""
        return self._email
    
    def get_name(self):
        """Return the full name."""
        return self._name
    
    def get_rfc2822_address(self):
        """Return the RFC 2822 address for this identity (e.g. 'John Smith
        <smith@example.com>').
        
        """
        return formataddr((self._name, self._email))

    def sendmail(self, to, message):
        """Send mail to one or more recipients. The required arguments are a
        list of RFC 822 to-address strings (a bare string will be treated as a
        list with 1 address), and a message string.

        """

        # If we were passed a bare string as the To: address, convert it to
        # a single element list.
        if isinstance(to, str):
            to = [ to, ]

        # Send one email with the appropriate recipient list.
        server = self._smtp_server()
        server.sendmail(self.get_rfc2822_address(), to, message)
        server.quit()

    def save_to_config(self, config = Config()):
        config.set('user', 'name', self._name)
        config.set('user', 'email', self._email)

        self._interface.new_section()
        self._interface.message("""
            Your default identity has been saved to the configuration.

            If you want to modify this information at any future time, you can do
            so with the following command:

            %s --set identity""" % os.path.basename(sys.argv[0]))

    def _smtp_server(self):
        """Return a smtplib SMTP object correctly initialised and connected to
        a SMTP server suitable for sending email on behalf of the user."""

        import smtplib

        self._interface.message("""Attempting to send via GMail. Enter
        your GMail address, for example 'steve@gmail.com', and your
        password.""")

        usernm = self._interface.input('Username')
        passwd = self._interface.input('Password', no_echo=True)

        # Add the '@gmail.com' part if omitted.
        if '@' not in usernm:
            usernm += '@gmail.com'

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(usernm, passwd)

        return server

