from collections import defaultdict
from SSN_element import SSN_element
from SSNRoom import SSNRoom


class SSNClient(SSN_element):
    """a wrapper class for client to add social network state variables"""
    def __init__(self, client, landing_room):
        super().__init__(client)
        # default dict allows appending to lists directly
        self.other_rooms_messages = defaultdict(list)
        self.landing_room = landing_room

    def load(self, room_id_alias):
        self.current_room = SSNRoom(self.join_room(self.landing_room), self.init_msg_hist_for_room)

    def on_message(self, room, event):
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                if self.is_room_setup and not self.rendered:
                    print("{0} joined".format(event['content']['displayname']))
                    self.rendered = True
                else:
                    room.events.pop( )

        elif event['type'] == "m.room.message":
            self.send_room_message(room, event)
        self.rendered = False






