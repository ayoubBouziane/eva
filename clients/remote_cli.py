#!/usr/bin/python3
"""
A command line interface Eva client that goes through the Eva MongoDB database
to send and receive messages. This client should work across the internet
provided the MongoDB instance is accessible.
"""

from pymongo import MongoClient
from anypubsub import create_pubsub_from_settings
from cli import CLI

class RemoteCLI(CLI):
    """
    Very similar to the LocalCLI class except that it requires a working Eva
    server and an accessible MongoDB instance holding the Eva database.
    """
    def __init__(self, host='localhost', port=27017, username='', password=''):
        super(RemoteCLI, self).__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pubsub = self.get_pubsub()

    def get_pubsub(self):
        """
        Overriden method that returns the pubsub instance required to
        send/receive messages to/from Eva.

        :return: The pubsub object used to publish Eva messages to the clients.
        :rtype: `anypubsub.interfaces.PubSub  <https://github.com/smarzola/anypubsub>`_
        """
        uri = 'mongodb://'
        if len(self.username) > 0:
            uri = uri + self.username
            if len(self.password) > 0:
                uri = uri + ':' + self.password + '@'
            else:
                uri = uri + '@'
        uri = '%s%s:%s' %(uri, self.host, self.port)
        client = MongoClient(uri)
        return create_pubsub_from_settings({'backend': 'mongodb',
                                            'client': client,
                                            'database': 'eva',
                                            'collection': 'communications'})

    def get_results(self, command):
        """
        Overriden method that handles user input by sending the query/command
        to the Eva MongoDB instance. These messages are processed by Eva and
        a response is generated - which is then picked up by the client in
        a consumer thread.

        :param command: The query/command to send Eva.
        :type command: string
        """
        self.pubsub.publish('eva_commands', {'input_text': command})

def main():
    """
    Start a RemoteCLI instance.
    """
    cli = RemoteCLI()
    # Subscribe to messages and command responses.
    cli.start_consumer('eva_messages')
    cli.start_consumer('eva_responses', 'Eva Response: ')
    cli.interact()

if __name__ == '__main__':
    main()
