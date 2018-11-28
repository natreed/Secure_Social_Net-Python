from matrix_client.client import MatrixClient, Room
from enum import Enum

class RoomType(Enum):
    CHAT = 1
    WALL = 2
    POST = 3


class SSNRoom(object):
    """Room wrapper to add extra state."""
    def __init__(self, room, update_parent):
        """update_parent is a function called when room is first joined.
        this will add the message history to the rooms and will be saved in the wall
        record. The wall record will be a json object stored in a room event in the
        wall point of entry room."""
        self.room = room
        self.room_type = None
        self.msg_store = []
        """"""
        for index, e in enumerate(self.room.get_events()):
            if e['type'] == 'm.room.message'\
                    and len(e['content']['body']) > 0\
                    and e['content']['body'][0] != '{':
                self.msg_store.append("{0}: {1}".format(
                    e['sender'], e['content']['body']))
            else:
                # we don't need to know non-message events before logon
                self.room.events.pop(index)
                # print(popped)
        update_parent(self.room.name, self.msg_store)

    def set_room_name(self, name):
        return self.room.set_room_name(name)

    def get_room_name(self):
        return self.room.name

    def get_room_id(self):
        return self.room.room_id

    def leave_room(self):
        return self.room.leave()




