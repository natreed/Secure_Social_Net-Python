from collections import defaultdict
from SSN_element import SSN_element


class SSNClient(SSN_element):
    """a wrapper class for client to add social network state variables"""

    def __init__(self, client):
        super().__init__(client)
        self.is_viewing_wall = False
        self.is_room_setup = False
        # default dict allows appending to lists directly
        self.other_rooms_messages = defaultdict(list)

    def add_post(self, room, event):
        """
        Post to current room.
        :param room:
        :param event:
        :return:
        """
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





