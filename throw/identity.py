"""Manage the user's identity."""

import logging
import sys
import os
import smtplib

from copy import copy

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
                    email_ = config.get('user', 'email'),
                    **config.get_section('smtp'))

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
        new_identity.send_test_email()

    return new_identity

class Identity(object):
    """An identity suitable for sending email from. This contains both
    the user's full name, email address and SMTP information."""

    __log = logging.getLogger(__name__ + '.Identity')

    def __init__(self, name, email_,
                 use_ssl = False, use_tls = False,
                 username = None, password = None, **kwargs):
        """Initialise an identity. The remain keyword arguments hold the SMTP
        server connection information. All fields are optional and are in
        effect passed to smtplib. The fields are:
        
            - host: The hostname of the SMTP server.
            - port: The port used to connect to the server.
            - username: The username to authenticate to the SMTP server with.
            - password: The password to authenticate to the SMTP server with.
            - use_ssl: Connect via SSL (default: no).
            - use_tls: Attempt to make use of the STARTTLS command (default: no).
        
        If use_ssl is True, try to connect to the SMTP server via SSL.
            
        """

        self._interface = TerminalInterface()
        self._name = name
        self._email = email_

        # Defaults
        self._smtp_vars = { }
        self._use_ssl = use_ssl
        self._use_tls = use_tls

        if username is not None:
            self._credentials = (username, password)
        else:
            self._credentials = None

        # Copy the SMTP vars
        for key in ['host', 'port']:
            if key in kwargs:
                self._smtp_vars[key] = kwargs[key]

        Identity.__log.info('Initialised identity "%s".' % self.get_rfc2822_address())
        Identity.__log.info('SMTP server options: %s' % self._smtp_vars)
        Identity.__log.info('Security options: SSL: %s, TLS: %s' % (self._use_ssl, self._use_tls))

        if self._credentials is not None:
            Identity.__log.info('Security credentials: username: %s, password: %s' % (
                self._credentials[0], self._credentials[1] is not None))
    
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

    def send_test_email(self):
        message = MIMEText('This is an example email from throw.')
        message['Subject'] = 'A test email from throw'
        message['To'] = self.get_rfc2822_address()
        message['From'] = self.get_rfc2822_address()

        try:
            self.sendmail(
                self.get_rfc2822_address(),
                message.as_string())
            self._interface.message('Test email sent')
        except smtplib.SMTPException as e:
            self._interface.error('Failed to send test email: the SMTP server said "%s".' % e)
        except Exception as e:
            self._interface.error('Failed to send test email: "%s".' % e)

    def _smtp_server(self):
        """Return a smtplib SMTP object correctly initialised and connected to
        a SMTP server suitable for sending email on behalf of the user."""

        if self._use_ssl:
            server = smtplib.SMTP_SSL(**self._smtp_vars)
        else:
            server = smtplib.SMTP(**self._smtp_vars)

        # server.connect()

        if self._use_tls:
            server.starttls()

        if self._credentials is not None:
            (user, passwd) = self._credentials

            if passwd is None:
                passwd = self._interface.input('Password for %s' % (user,), no_echo=True)
                
            server.login(user, passwd)

        return server

