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
import os
from subprocess import call
from enum import Enum
from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError
from requests.exceptions import MissingSchema
from SSNClient import SSNClient
import json
from Wall import Wall
import pickle
import copy


class SSN(object):
    def __init__(self, host, username, password, landing_room):
        self.m_client = MatrixClient(host)
        self.login(username, password)
        # Wall and chat client hold state for themselves respectively.
        # They share a common base class, 'ssn_element'
        self.wall = self.start_wall()
        """Thsi is cool. Wall store stores the state, so if we want to see a friend's wall, we can have 
        them send us their wall state and build it for ourselves."""
        if os.stat("./Stores/Wall_Store.txt").st_size != 0:
            with open('Stores/Wall_Store.txt') as json_file:
                # raw_data = json_file.read()
                # wall_store = pickle.loads(raw_data) # deserialization
                wall_store = json.load(json_file)
                self.wall.initialize_from_file(wall_store["friends"],
                                               wall_store["posts"])

        self.chat_client = self.start_ssn_client()
        """Current interface is the context/interface of the current 'ssn_element'.
        The chat client is the base context. To access any other context element
        The user will first have to return to the base context. This is to keep context
        switching programmatically simple. Once the complexity increases with more element_types
        a stack will be used to keep an ordering. So that when the user leaves one context
        the previous context will be loaded."""
        self.current_interface = self.chat_client
        """Landing room is the room of entry."""
        self.landing_room = landing_room

    def render_wall(self):
        self.current_interface = self.wall
        # call('clear')
        username = self.m_client.user_id.split(':')[0][1:]
        print("Welcome to {0}'s wall!".format(username))
        if self.wall.current_room == None:
            self.wall.load()

    def render_client(self):
        self.current_interface = self.chat_client
        # call('clear')
        self.current_interface.join_room(self.current_interface.current_room.room_id)
        print("Welcome back to the client!")

    def start_ssn_client(self):
        return SSNClient(self.m_client)

    def start_wall(self):
        wall = Wall(self.m_client)
        wall.load()
        return wall

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

    def input_controller(self, msg):
        args = msg.split()
        cmd = args.pop(0).lstrip('/')
        if cmd == "q":
            # TODO: Right now, q is how to switch from wall context back to base
            if self.current_interface == self.wall:
                self.render_client()
                return
            else:
                self.wall.leave()  # stores wall state
                print("Goodbye")
                sys.exit(0)
        # TODO: This is going to get messy if we add other SSN elements.
        elif cmd == "sw" or cmd == 'show_wall':
            self.render_wall()
        if self.current_interface == self.wall or cmd:
            self.wall_input_handler(cmd, args)
        else:
            self.client_input_handler(cmd, args)

    def client_input_handler(self, cmd, args):
        if cmd == 'join_room' or cmd == 'j':
            msg = ' '.join(args)
            self.current_interface.join_room("#{0}:matrix.org".format(msg))
        elif cmd == "show_rooms" or cmd == 's':
            self.current_interface.show_rooms()
        elif cmd == "invite_friend" or cmd == 'i':
            self.current_interface.add_friend(' '.join(args))
        else:
            print("{0} has no implementation in chat service client".format(cmd))

    def wall_input_handler(self, cmd, args):
        # TODO: For initial develpment only allow viewing self.wall
        # TODO: Sending message to a room is not a real solution
        # TODO: Allowing friends will require adding a new m.type to Client-Server API
        if cmd == "show_wall" or cmd == "sw":
            """send a message of type text for now"""
            self.current_interface.current_room.send_text('show_wall')
        elif cmd == "post" or cmd == "p":
            data = {"add_post": ' '.join(args)}
            self.current_interface.current_room.send_text(json.dumps(data))
        elif cmd == "pc" or cmd == "comment":
            """post comment takes 2 args (post_id, comment)
                    for example <pc 2 give me a break"""
            id = args.pop(0)
            if id.isdigit():
                data = {"comment": ' '.join(args), "post_id": id}
                self.current_interface.current_room.send_text(json.dumps(data))
            else:
                print("The second argument must be an id <integer value>")
        else:
            print(format("Did not recognize the command: {0}").format(cmd))

    def run(self):
        self.current_interface.join_room(self.landing_room)

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

        self.current_interface.m_client.start_listener_thread()

        while True:
            msg = input()
            if msg.startswith('/'):
                self.input_controller(msg)
            else:
                self.current_interface.current_room.send_text(msg)

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


if __name__ == '__main__':
    SSN('http://www.matrix.org', '@natreed:matrix.org', 'vatloc4evr', '#my_room:matrix.org').run()
