from collections import defaultdict
import sys
from matrix_client.api import MatrixRequestError
from matrix_client.client import MatrixClient, Room

class SSN_element(object):
    def __init__(self, client):
        self.m_client = client
        """Additional state for SSN"""
        self.current_room = None
        self.friends = {}
        self.is_room_setup = False
        # default dict allows appending to lists directly
        self.other_rooms_messages = defaultdict(list)

    @classmethod
    def on_message(cls, room, event):
        raise NotImplementedError

    @classmethod
    def add_post(cls, room, event):
        raise NotImplementedError

    def add_friend(self, user_id):
        if user_id not in self.friends.keys():
            self.friends[user_id] = ''
            print("added friend")
        else:
            print(format("{0} is already on the list.", user_id))

    def get_current_room(self):
        return self.current_room

    def join_room(self, room_id_alias):
        """
        :param client:
        :param room_id_alias:
        :return matrix room object:
        """
        try:
            self.is_room_setup = False
            self.current_room = self.m_client.join_room(room_id_alias)
            self.current_room.add_listener(self.on_message)
            self.current_room.name = room_id_alias.split(':')[0].lstrip('#')
            self.current_room.backfill_previous_messages()
            self.is_room_setup = True

        except MatrixRequestError as e:
            print(e)
            if e.code == 400:
                print("Room ID/Alias in the wrong format")
                sys.exit(11)
            else:
                print("Couldn't find room.")
                sys.exit(12)
        return self.current_room


