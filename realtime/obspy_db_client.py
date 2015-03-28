#!/usr/bin/env python

from obspy.db.client import Client

class PimsClient(Client):
    """
    Client for database created by PIMS packetGrabber (instead of obspy.db).
    """
    def __init__(self, url=None, session=None, debug=False):
        super(PimsClient, self).__init__(url, session, debug)
        """
        Initializes the client.

        :type url: string, optional
        :param url: A string that indicates database dialect and connection
            arguments. See
            http://docs.sqlalchemy.org/en/latest/core/engines.html for more
            information about database dialects and urls.
            
        :type session: class:`sqlalchemy.orm.session.Session`, optional
        :param session: An existing database session object.
        
        :type debug: boolean, optional
        :param debug: Enables verbose output.
        """
        super(PimsClient, self).__init__(url, session, debug)
        self.extra_stuff = 'extra_stuff'
