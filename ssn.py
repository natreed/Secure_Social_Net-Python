#!/usr/bin/env python3

"""# A simple chat client for matrix.
# This sample will allow you to connect to a room, and send/recieve messages.
# Args: host:port username password room
# Error Codes:
# 1 - Unknown problem has occured
# 2 - Could not find the server.
# 3 - Bad URL Format.
# 4 - Bad username/password.
# 11 - Wrong room format.
# 12 - Couldn't find room.
"""


import sys
import os
from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError
from requests.exceptions import MissingSchema
from SSNChat import SSNChat
import json
from SSNWall import SSNWall
from WallRoom import WallRoom
from time import sleep
import subprocess
import shlex

class ssn():
    """ssn is the controller for different app elements"""
    def __init__(self, host, username, password, landing_room):
        self.m_client = MatrixClient(host)
        self.login(username, password)
        # for cleanup of orphaned and abandoned rooms
        # self.remove_empty_rooms(self.m_client)
        self.chat_landing_room = landing_room
        self.user_id = username.split(':')[0][1:]
        self.wall_landing_room = "#{}_w:matrix.org".format(self.user_id)
        # make sure rooms have names
        for room in self.m_client.rooms.values():
            room_name = room.display_name.split(':')[0].lstrip('#')
            room.set_room_name(room_name)
        self.wall = self.start_wall()
        # SSN element for rendering friend's wall
        self.friend_wall = None
        """This is cool. Wall store stores the state, so if
        we want to see a friend's wall, we can have
        them send us their wall state and build it for ourselves."""
        if os.stat("./Stores/Wall_Store.txt").st_size != 0:
            with open('Stores/Wall_Store.txt', 'r+') as json_file:
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

    def render_wall(self):
        """changes context to wall"""
        self.current_interface = self.wall
        # call('clear')
        username = self.m_client.user_id.split(':')[0][1:]
        print("Welcome to {0}'s wall!".format(username))
        self.wall.load()

    def render_client(self):
        """changes context to chat"""
        self.current_interface = self.chat_client.load(self.chat_landing_room)
        print("Welcome back to the client!")

    def start_ssn_client(self):
        """this function is just for the sake of being explicit"""
        return SSNChat(self.m_client, self.chat_landing_room)

    def start_wall(self):
        """for readability"""
        wall = SSNWall(self.m_client, self.wall_landing_room)
        wall.load()
        return wall

    def login(self, username, password):
        """
        :param username:
        :param password:
        :return:
        """
        try:
            self.m_client.login(username, password, limit=100, sync=True)
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
            self.wall.update_wall_store()  # stores wall state
            self.wall.update_wall_state()
            print("Goodbye")
            # sys.exit(0)
        elif cmd in ('sw', 'show_wall'):
            if self.current_interface != self.wall:
                self.render_wall()
        elif cmd in ('sw', 'show_chat'):
            if self.current_interface != self.chat_client:
                self.render_client()
        if self.current_interface == self.wall:
            self.wall_input_handler(cmd, args)
        else:
            self.client_input_handler(cmd, args)

    def client_input_handler(self, cmd, args):
        """
        Called for messages recieved while in client context.
        :param cmd:
        :param args:
        :return:
        """
        if cmd in ('join_room', 'j'):
            msg = ' '.join(args)
            self.current_interface.load("#{0}:matrix.org".format(msg))

        elif cmd in ('show_rooms', 's'):
            self.current_interface.show_rooms()
        elif cmd == "invite_friend" or cmd == 'i':
            self.current_interface.add_friend(' '.join(args))
        else:
            print("{0} has no implementation in chat service client".format(cmd))

    def remove_empty_rooms(self, MatrixClient):
        """
        removes all empty rooms from m_client
        :return:
        """
        for room_id, room in MatrixClient.rooms.items():
            if len(room.aliases) != 0:
                alias = room.aliases[0].split(':')[0][1:]
                if alias.startswith('#'):
                    MatrixClient.api.leave_room(room.room_id)
        return MatrixClient

    def wall_input_handler(self, cmd, args):
        """
        Called for messages received while in wall context
        :param cmd:
        :param args:
        :return:
        """
        if cmd == "show_wall" or cmd == "sw":
            """send a message of type text for now"""
            self.current_interface.current_room.room.send_notice('show_wall')

        elif cmd == "post" or cmd == "p":
            data = {"add_post": ' '.join(args)}
            self.current_interface.current_room.room.send_notice(json.dumps(data))
        elif cmd == "pc" or cmd == "comment":
            """post comment takes 1 args (post_id)
                    for example <pc 2>"""
            if len(args) > 0:
                post_id = args.pop(0)
            else:
                print("post id number must be included as an argument.")
                return
            if post_id.isdigit():
                data = {"comment_post": post_id}
                self.current_interface.current_room.room.send_notice(json.dumps(data))
            else:
                print("The second argument must be an id <integer value>")
        elif cmd == "rp" or cmd == "remove_post":
            id = args.pop(0)
            if id.isdigit:
                data = {"remove_post": id}
                self.current_interface.current_room.room.send_notice(json.dumps(data))
        else:
            print(format("Did not recognize the command: {0}").format(cmd))

    def listen(self):

        while True:
            # Spin wait if there is no room ready for input
            room = self.current_interface.current_room
            if room:
                msg = input()
                sleep(.1)
                # print(msg)
                if msg.startswith('/'):
                    self.input_controller(msg)
                else:
                    if type(room) == WallRoom and room.get_room_name() == self.user_id + "_w":
                        continue
                    else:
                        self.current_interface.current_room.room.send_text(msg)

    def run(self):

        self.current_interface.load(self.chat_landing_room)
        self.current_interface.m_client.start_listener_thread()
        self.listen()


if __name__ == '__main__':
    ssn('http://www.matrix.org', '@natreed:matrix.org', 'vatloc4evr', '#my_room:matrix.org').run()
