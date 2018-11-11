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
from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError
from requests.exceptions import MissingSchema
from SSNClient import SSNClient
import json
from Wall import Wall

class SSN(object):
    def __init__(self, host, username, password):
        self.m_client = MatrixClient(host)
        self.login(username, password)
        self.context_options = {"basic": SSNClient(self.m_client), "wall": Wall(self.m_client)}
        self.client_context = self.context_options["basic"]

    def login(self, username, password):
        try:
            self.m_client.login(username, password, limit=10, sync=True)
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
        if cmd == 'join_room' or cmd == 'j':
            msg = ' '.join(args)
            self.client_context.join_room("#{0}:matrix.org".format(msg))

        elif cmd == "q":

            print("Goodbye")
            sys.exit(0)
        elif cmd == "show_rooms" or cmd == 's':
            self.client_context.show_rooms()
        elif cmd == "invite_friend" or cmd == 'i':
            self.client_context.add_friend(' '.join(args))
        # TODO: For initial develpment only allow viewing self.wall
        # TODO: Sending message to a room is not a real solution
        # TODO: Allowing friends will require adding a new m.type to Client-Server API
        elif cmd == "show_wall" or cmd == "sw":
            """send a message of type text for now"""
            self.Wall.current_room.send_text('show_wall')
        elif cmd == "post" or cmd == "p":
            data = {format(' '.join(args))}
            self.Wall.current_room.send_text(json.dumps(data))
        else:
            print(format("Did not recognize the command: {0}").format(cmd))


if __name__ == '__main__':
    ssn = SSN('http://www.matrix.org', '@natreed:matrix.org', 'vatloc4evr')
    client = ssn.client_context
    room_name = '#my_room:matrix.org'
    client.join_room(room_name)

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

    client.m_client.start_listener_thread()

    while True:
        msg = input()
            #samples_common.get_input()
        if msg.startswith('/'):
            ssn.input_handler(msg)
        else:
            client.current_room.send_text(msg)

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
