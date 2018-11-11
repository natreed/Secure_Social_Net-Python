import sys
from subprocess import call
from matrix_client.api import MatrixRequestError

from collections import defaultdict
from Wall import Wall
import json
from SSN_element import SSN_element


class SSNClient(SSN_element):
    """a wrapper class for client to add social network state variables"""

    def __init__(self, client):
        super().__init__(client)
        self.is_viewing_wall = False
        self.is_room_setup = False
        # default dict allows appending to lists directly
        self.other_rooms_messages = defaultdict(list)

        for room in self.m_client.rooms.values():
            room.set_room_name(room.display_name.split(':')[0].lstrip('#'))
            self.other_rooms_messages[room.display_name] = []

    def show_rooms(self):
        for room in self.m_client.rooms.values():
            print(room.display_name)

    def add_post(self, room, event):
        if event['content']['msgtype'] == "m.text":
            if room.display_name == self.current_room.display_name:
                print("{0}: {1}: {2}".format(room.name, event['sender'], event['content']['body']))
            else:
                self.other_rooms_messages[room.name].append("{0}: {1}: {2}"
                                                            .format(room.name, event['sender'],
                                                                    event['content']['body']))

    def send_wall_image(self, event):
        print("not yet implemented. coming soon")
        return

    # TODO: Listener will need to handle post comments to multiple posts. Not just current post.
    def on_message(self, room, event):
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                print("{0} joined".format(event['content']['displayname']))
        elif event['type'] == "m.room.message":
                self.add_post(room, event)
        else:
            print(event['type'])
        return





