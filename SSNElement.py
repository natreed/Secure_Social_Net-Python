import sys
from collections import defaultdict
from matrix_client.api import MatrixRequestError
import time


class SSNElement:
    def __init__(self, client, landing_room):
        self.m_client = client
        """Additional state for SSN"""
        self.current_room = None
        self.landing_room = landing_room
        self.friends = {}
        # the room table matches the room name to the to the room id
        self.room_table = {}
        self.is_room_setup = False
        # default dict allows appending to lists directly
        # a store for all the messages {room:[list of messages], ...}
        # updates occur in send_room message
        self.all_rooms_messages = defaultdict(defaultdict)
        self.loaded_rooms = {}
        self.update_room_table()
        self.rendered = False



    @classmethod
    def on_message(cls, room, event):
        raise NotImplementedError

    @classmethod
    def load(cls, **kwargs):
        raise NotImplementedError

    def init_msg_hist_for_room(self, room_name, msg_store):
        for msg in msg_store:
            """making timestamp key should avoid duplicates"""
            self.all_rooms_messages[room_name][time.time()] = msg
            print(msg)

    def send_room_message(self, room, event, prepend=None):
        """
        :param room:
        :param event:
        :param prepend:
        :return:
        """
        if event['content']['msgtype'] == "m.text":
            msg = "{0}: {1}".format(event['sender'], event['content']['body'])
            if prepend:
                msg = prepend + msg
            if self.is_room_setup and room.name == self.current_room.room.name:
                print(msg)

            self.all_rooms_messages[room.name][time.time] = "\t" + msg

    def show_rooms(self):
        for room in self.m_client.rooms.values():
            print(room.name)

    def add_friend(self, user_id):
        if user_id not in self.friends.keys():
            self.friends[user_id] = ''
            print("added friend")
        else:
            print(format("{0} is already on the list.", user_id))

    def get_current_room(self):
        return self.current_room

    def update_room_table(self):
        for id, room in self.m_client.rooms.items():
            self.room_table[room.name] = id

    def join_room(self, room_id_alias=None, print_room=True):
        """
        :param room_id_alias:
        :return matrix room object:
        """
        try:
            self.is_room_setup = False
            room = self.m_client.join_room(room_id_alias)
            # this sets the user profile for the client that is specific to the room
            room.set_user_profile(displayname=self.m_client.user_id.split(':')[0][1:])
            room.set_room_name(room_id_alias.split(':')[0].lstrip('#'))
            if print_room:
                print("CURRENT ROOM: {}".format(room.name.upper()))
            room.backfill_previous_messages()
            self.is_room_setup = True
            for msg in self.all_rooms_messages[room.name].values():
                print(msg)
            room.add_listener(self.on_message)

        except MatrixRequestError as e:
            print(e)
            if e.code == 400:
                print("Room ID/Alias in the wrong format")
                sys.exit(11)
            else:
                print("Couldn't find room.")
                sys.exit(12)

        return room


