import sys
from collections import defaultdict
from matrix_client.api import MatrixRequestError


class SSN_element(object):
    def __init__(self, client):
        self.m_client = client
        """Additional state for SSN"""
        self.current_room = None
        self.friends = {}
        # the room table matches the room name to the to the room id
        self.room_table = {}
        self.is_room_setup = False
        # default dict allows appending to lists directly
        # a store for all the messages {room:[list of messages], ...}
        # updates occur in send_room message
        self.all_rooms_messages = defaultdict(list)
        self.update_room_table()
        # TODO: NOT YET IMPLEMENTED list of visited rooms appended to each time a room is joined.
        # when client leaves room we can pop() and join the previous room on the list.
        self.rooms_visited = []
        self.rendered = False
        for room in self.m_client.rooms.values():
            room.set_room_name(room.display_name.split(':')[0].lstrip('#'))
            self.all_rooms_messages[room.display_name] = []

    @classmethod
    def on_message(cls, room, event):
        raise NotImplementedError

    def load(self, **kwargs):
        raise NotImplementedError

    def init_msg_hist_for_room(self, room_name, msg_store):
        for msg in msg_store:
            self.all_rooms_messages[room_name].append(msg)

    def send_room_message(self, room, event, prepend=None):
        """
        :param room:
        :param event:
        :param prepend:
        :return:
        """
        if event['content']['msgtype'] == "m.text":
            msg = "{0}: {1}: {2}".format(room.name, event['sender'], event['content']['body'])
            if prepend:
                msg = prepend + msg
            if self.is_room_setup and room.name == self.current_room.room.name:
                print(msg)

            self.all_rooms_messages[room.name].append(msg)




    def wrap(self, callback):
        return callback

    def update_wall_store(self):
        """TODO: This is just a placeholder for now.
        This func may not be necessary"""
        return

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

    def join_room(self, room_id_alias=None, prepend=None):
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
            print("CURRENT ROOM: {}".format(room.name.upper()))
            if prepend:
                room.set_room_name(prepend + room.name)
            room.backfill_previous_messages()
            self.is_room_setup = True
            for event in room.events:
                if event['type'] == 'm.room.message' and event['content']['msgtype'] == "m.text":
                    print("{0}: {1}: {2}".format(room.name, event['sender'], event['content']['body']))
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



