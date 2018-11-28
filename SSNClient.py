from collections import defaultdict
from SSNElement import SSNElement
from SSNRoom import SSNRoom


class SSNClient(SSNElement):
    """a wrapper class for client to add social network state variables"""
    def __init__(self, client, landing_room):
        super().__init__(client, landing_room)
        # default dict allows appending to lists directly
        self.other_rooms_messages = defaultdict(list)

    def load(self, room_id_alias):
        room_name = room_id_alias.split(':')[0][1:]
        if room_name not in self.loaded_rooms.keys():
            self.current_room = SSNRoom(self.join_room(self.landing_room), self.init_msg_hist_for_room)
            self.loaded_rooms[self.current_room.get_room_name()] = self.current_room
        else:
            self.current_room = self.loaded_rooms[room_name]
            for msg in self.all_rooms_messages[room_name].values():
                print(msg)

    def on_message(self, room, event):
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                if self.is_room_setup and not self.rendered:
                    print("{0} joined".format(event['content']['displayname']))
                    self.rendered = True

        elif event['type'] == "m.room.message":
            self.send_room_message(room, event)
        self.rendered = False






