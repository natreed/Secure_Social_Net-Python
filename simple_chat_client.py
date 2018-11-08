#!/usr/bin/env python3

# A simple chat client for matrix.
# This sample will allow you to connect to a room, and send/recieve messages.
# Args: host:port username password room
# Error Codes:
# 1 - Unknown problem has occured
# 2 - Could not find the server.
# 3 - Bad URL Format.
# 4 - Bad username/password.
# 11 - Wrong room format.
# 12 - Couldn't find room.

import sys
import samples_common  # Common bits used between samples
from subprocess import call
from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema
from collections import defaultdict


class CLClient(object):
    def __init__(self, host, username, password):
        self.client = MatrixClient(host)
        self.login(username, password)
        self.current_room = None
        #default dict allows appending to lists directly
        self.other_rooms_messages = defaultdict(list)
        for room in self.client.rooms.keys():
            self.other_rooms_messages[room] = []
        self.other_rooms_messages['blue_wave'] = []

        # for room in self.client.rooms.values():
        # room.add_listener(on_message)

    # Called when a message is recieved.
    def on_message(self, room, event):
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                print("{0} joined".format(event['content']['displayname']))
        # TODO: store messages from other rooms in other_rooms_messages
        elif event['type'] == "m.room.message":
            if event['content']['msgtype'] == "m.text":
                if room.display_name == self.current_room.display_name:
                    print("{0}: {1}: {2}".format(room.display_name, event['sender'], event['content']['body']))
                # else:
                #     self.other_rooms_messages[room.display_name].append("{0}: {1}: {2}"
                #                                                         .format(room.display_name, event['sender'],
                #                                                                 event['content']['body']))
        else:
            print(event['type'])
        return

    def join_room(self, room_id_alias, client):
        """
        :param client:
        :param room_id_alias:
        :return matrix room object:
        """
        try:
            self.current_room = client.join_room(room_id_alias)
            self.current_room.add_listener(self.on_message)
            self.current_room.name = room_id_alias.split(':')[0].lstrip('#')
            call('clear')
            self.current_room.backfill_previous_messages()

        except MatrixRequestError as e:
            print(e)
            if e.code == 400:
                print("Room ID/Alias in the wrong format")
                sys.exit(11)
            else:
                print("Couldn't find room.")
                sys.exit(12)
        return self.current_room

    def login(self, username, password):
        try:
            self.client.login(username, password, limit=10, sync=True)
        except MatrixRequestError as e:
            print(e)
            if e.code == 403:
                print("Bad username or password.")
                sys.exit(4)
            else:
                print("Check your sever details are correct.")
                sys.exit(2)
        except MissingSchema as e:
            print("Bad URL format.")
            print(e)
            sys.exit(3)

    def input_handler(self, msg):
        args = msg.split()
        cmd = args.pop(0).lstrip('/')
        if cmd == 'join_room':
            if len(args) != 1:
                print("The join_room command only needs one argument: room_id/alias")
            else:
                self.join_room('#' + args.pop(0) + ':matrix.org', self.client)
        elif cmd == "quit":
            print("Goodbye")
            sys.exit(0)
        else:
            print(format("Did not recognize the command: {0}", cmd))

    def show_rooms(self):
        for room in self.client.rooms.keys():
            print(room)


if __name__ == '__main__':
    m_client = CLClient('http://www.matrix.org', '@natreed:matrix.org', 'vatloc4evr')
    client = m_client.client
    room = '#my_room:matrix.org'
    room_name = '#my_room:matrix.org'
    m_client.join_room(room_name, client)
    # room.add_listener(m_client.on_message)
    # #TODO: why are the aliases not showing?
    # room.name = room_name.split(':')[0].lstrip('#')
    # room.aliases.append(room_name.split(':')[0].lstrip('#'))
    #
    #
    # #testing room change to other room
    # print("room id before change: %s" % room.aliases[0])
    #
    # room = client.join_room('#other_room:matrix.org')
    # room.aliases.append(room_name.split(':')[0].lstrip('#'))
    # room.add_listener(m_client.on_message)
    # print("room id after change: %s" % room.room_id)
    #
    # #go back to my_room
    # room_name = '#my_room:matrix.org'
    # room = client.join_room(room_name)
    # room.add_listener(m_client.on_message)
    # room.aliases.append(room_name.split(':')[0].lstrip('#'))

    # #TODO: This is for testing changing rooms
    # self.client.create_room("other_room").add_listener(self.on_message)

    client.start_listener_thread()

    while True:
        msg = samples_common.get_input()
        if msg.startswith('/'):
            m_client.input_handler(msg)
        else:
            m_client.current_room.send_text(msg)

    # logging.basicConfig(level=logging.WARNING)
    # host, username, password = samples_common.get_user_details(sys.argv)
    #
    # if len(sys.argv) > 4:
    #     room_id_alias = sys.argv[4]
    # else:
    #     room_id_alias = samples_common.get_input("Room ID/Alias: ")

    # TODO: THESE VALUES ARE JUST FOR TESTING
    # client.main('http://www.matrix.org', '@natreed:matrix.org', 'vatloc4evr', '#my_room:matrix.org')
    # main(host, username, password, room_id_alias)
